"""Accounts indexer."""

import logging

from datetime import datetime
from toolz import partition_all

import ujson as json

from hive.db.adapter import Db
from hive.utils.normalize import rep_log10, vests_amount
from hive.utils.timer import Timer
from hive.utils.account import safe_profile_metadata
from hive.utils.unique_fifo import UniqueFIFO

from hive.indexer.db_adapter_holder import DbAdapterHolder

log = logging.getLogger(__name__)

DB = Db.instance()

class Accounts(DbAdapterHolder):
    """Manages account id map, dirty queue, and `hive_accounts` table."""

    _updates_data = {}

    inside_flush = False

    # name->id map
    _ids = {}

    # fifo queue
    _dirty = UniqueFIFO()

    # in-mem id->rank map
    _ranks = {}

    # account core methods
    # --------------------

    @classmethod
    def update_op(cls, update_operation):
        """Save json_metadata."""

        if cls.inside_flush:
            log.exception("Adding new update-account-info into '_updates_data' dict")
            raise RuntimeError("Fatal error")

        key = update_operation['account']
        cls._updates_data[key] = safe_profile_metadata( update_operation )

    @classmethod
    def load_ids(cls):
        """Load a full (name: id) dict into memory."""
        assert not cls._ids, "id map already loaded"
        cls._ids = dict(DB.query_all("SELECT name, id FROM hive_accounts"))

    @classmethod
    def clear_ids(cls):
        """Wipe id map. Only used for db migration #5."""
        cls._ids = None

    @classmethod
    def default_score(cls, name):
        """Return default notification score based on rank."""
        _id = cls.get_id(name)
        rank = cls._ranks[_id] if _id in cls._ranks else 1000000
        if rank < 200: return 70    # 0.02% 100k
        if rank < 1000: return 60   # 0.1%  10k
        if rank < 6500: return 50   # 0.5%  1k
        if rank < 25000: return 40  # 2.0%  100
        if rank < 100000: return 30 # 8.0%  15
        return 20

    @classmethod
    def get_id(cls, name):
        """Get account id by name. Throw if not found."""
        assert isinstance(name, str), "account name should be string"
        assert name in cls._ids, 'Account \'%s\' does not exist' % name
        return cls._ids[name]

    @classmethod
    def exists(cls, name):
        """Check if an account name exists."""
        if isinstance(name, str):
            return name in cls._ids
        return False

    @classmethod
    def register(cls, name, op_details, block_date, block_num):
        """Block processing: register "candidate" names.

        There are four ops which can result in account creation:
        *account_create*, *account_create_with_delegation*, *pow*,
        and *pow2*. *pow* ops result in account creation only when
        the account they name does not already exist!
        """

        if name is None:
            return

        # filter out names which already registered
        if cls.exists(name):
            return

        profile = safe_profile_metadata( op_details )

        DB.query("""INSERT INTO hive_accounts (name, created_at, display_name, about, location, website, profile_image, cover_image )
                  VALUES (:name, :date, :display_name, :about, :location, :website, :profile_image, :cover_image )""",
                  name=name, date=block_date, display_name = profile['name'], about = profile['about'],
                  location = profile['location'], website = profile['website'],
                  profile_image = profile['profile_image'], cover_image = profile['cover_image'] )

        # pull newly-inserted ids and merge into our map
        sql = "SELECT id FROM hive_accounts WHERE name = :name"
        cls._ids[name] = DB.query_one(sql, name=name)

        # post-insert: pass to communities to check for new registrations
        from hive.indexer.community import Community, START_DATE
        if block_date > START_DATE:
            Community.register(name, block_date, block_num)

    # account cache methods
    # ---------------------

    @classmethod
    def dirty(cls, account):
        """Marks given account as needing an update."""
        return cls._dirty.add(account)

    @classmethod
    def dirty_set(cls, accounts):
        """Marks given accounts as needing an update."""
        return cls._dirty.extend(accounts)

    @classmethod
    def dirty_all(cls):
        """Marks all accounts as dirty. Use to rebuild entire table."""
        cls.dirty(set(DB.query_col("SELECT name FROM hive_accounts")))

    @classmethod
    def dirty_oldest(cls, limit=50000):
        """Flag `limit` least-recently updated accounts for update."""
        sql = "SELECT name FROM hive_accounts ORDER BY cached_at LIMIT :limit"
        return cls.dirty_set(set(DB.query_col(sql, limit=limit)))

    @classmethod
    def flush_online(cls, steem, trx=False, spread=1):
        """Process all accounts flagged for update.

         - trx: bool - wrap the update in a transaction
         - spread: int - spread writes over a period of `n` calls
        """
        accounts = cls._dirty.shift_portion(spread)

        count = len(accounts)
        if not count:
            return 0

        if trx:
            log.info("[SYNC] update %d accounts", count)

        cls._cache_accounts(accounts, steem, trx=trx)
        return count

    @classmethod
    def _cache_accounts(cls, accounts, steem, trx=True):
        """Fetch all `accounts` and write to db."""
        timer = Timer(len(accounts), 'account', ['rps', 'wps'])
        for name_batch in partition_all(1000, accounts):
            cached_at = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

            timer.batch_start()
            batch = steem.get_accounts(name_batch)

            timer.batch_lap()
            sqls = [cls._sql(acct, cached_at) for acct in batch]
            DB.batch_queries(sqls, trx)

            timer.batch_finish(len(batch))
            if trx or len(accounts) > 1000:
                log.info(timer.batch_status())

    @classmethod
    def _sql(cls, account, cached_at):
        """Prepare a SQL query from a steemd account."""
        vests = vests_amount(account['vesting_shares'])

        #Not used. The member `vote_weight` from `hive_accounts` is removed.
        # vote_weight = (vests
        #                + vests_amount(account['received_vesting_shares'])
        #                - vests_amount(account['delegated_vesting_shares']))

        proxy_weight = 0 if account['proxy'] else float(vests)
        for satoshis in account['proxied_vsf_votes']:
            proxy_weight += float(satoshis) / 1e6

        # remove empty keys
        useless = ['transfer_history', 'market_history', 'post_history',
                   'vote_history', 'other_history', 'tags_usage',
                   'guest_bloggers']
        for key in useless:
            del account[key]

        # pull out valid profile md and delete the key
        profile = safe_profile_metadata(account)
        del account['json_metadata']
        del account['posting_json_metadata']

        values = {
            'name':         account['name'],
            'created_at':   account['created'],
            'proxy':        account['proxy'],
            'reputation':   rep_log10(account['reputation']),
            'proxy_weight': proxy_weight,
            'cached_at':    cached_at,

            'display_name':  profile['name'],
            'about':         profile['about'],
            'location':      profile['location'],
            'website':       profile['website'],
            'profile_image': profile['profile_image'],
            'cover_image':   profile['cover_image'],

            'raw_json': json.dumps(account)}

        # update rank field, if present
        _id = cls.get_id(account['name'])
        if _id in cls._ranks:
            values['rank'] = cls._ranks[_id]

        bind = ', '.join([k+" = :"+k for k in list(values.keys())][1:])
        return ("UPDATE hive_accounts SET %s WHERE name = :name" % bind, values)

    @classmethod
    def flush(cls):
        """ Flush json_metadatafrom cache to database """

        cls.inside_flush = True
        n = 0

        if cls._updates_data:
            cls.beginTx()

            for name, data in cls._updates_data.items():
              sql = """
                        UPDATE hive_accounts
                        SET
                          display_name = '{}',
                          about = '{}',
                          location = '{}',
                          website = '{}',
                          profile_image = '{}',
                          cover_image = '{}'
                        WHERE name = '{}'
                  """.format( data['name'], data['about'], data['location'], data['website'], data['profile_image'], data['cover_image'], name )
              cls.db.query(sql)

            n = len(cls._updates_data)
            cls._updates_data.clear()
            cls.commitTx()

        cls.inside_flush = False

        return n
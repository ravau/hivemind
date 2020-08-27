"""Handles building condenser-compatible response objects."""

import logging
#import ujson as json
import traceback

from hive.server.bridge_api.objects import _bridge_post_object
from hive.utils.post import post_to_internal
from hive.utils.normalize import sbd_amount
from hive.server.common.helpers import (
    #ApiError,
    return_error_info)

log = logging.getLogger(__name__)

ROLES = {-2: 'muted', 0: 'guest', 2: 'member', 4: 'admin', 6: 'mod', 8: 'admin'}

@return_error_info
async def get_post_header(context, author, permlink):
    """Fetch basic post data"""
    db = context['db']
    sql = """
        SELECT 
            hp.id, ha_a.name as author, hpd_p.permlink as permlink, hcd.category as category, depth
        FROM 
            hive_posts hp
        INNER JOIN hive_accounts ha_a ON ha_a.id = hp.author_id
        INNER JOIN hive_permlink_data hpd_p ON hpd_p.id = hp.permlink_id
        LEFT JOIN hive_category_data hcd ON hcd.id = hp.category_id
        WHERE ha_a.name = :author
            AND hpd_p.permlink = :permlink
            AND counter_deleted = 0
    """

    row = await db.query_row(sql, author=author, permlink=permlink)

    assert row, 'post \'@{}/{}\' does not exist'.format(author,permlink)

    return dict(
        author=row['author'],
        permlink=row['permlink'],
        category=row['category'],
        depth=row['depth'])


@return_error_info
async def normalize_post(context, post):
    """Takes a steemd post object and outputs bridge-api normalized version."""
    db = context['db']

    # load core md
    sql = """
        SELECT 
            hp.id, hcd.category as category, community_id, is_muted, is_valid
        FROM hive_posts hp
        INNER JOIN hive_accounts ha_a ON ha_a.id = hp.author_id
        INNER JOIN hive_permlink_data hpd_p ON hpd_p.id = hp.permlink_id
        LEFT JOIN hive_category_data hcd ON hcd.id = hp.category_id
        WHERE ha_a.name = :author AND hpd_p.permlink = :permlink
    """
    core = await db.query_row(sql, author=post['author'], permlink=post['permlink'])
    if not core:
        core = dict(id=None,
                    category=post['category'],
                    community_id=None,
                    is_muted=False,
                    is_valid=True)

    # load author
    sql = """SELECT id, reputation FROM hive_accounts WHERE name = :name"""
    author = await db.query_row(sql, name=post['author'])

    # append core md
    post['category'] = core['category']
    post['community_id'] = core['community_id']
    post['gray'] = core['is_muted']
    post['hide'] = not core['is_valid']

    # TODO: there is a bug in steemd.. promoted value returned as 0.000 LIQUID
    #       until it's promoted.. then returned as X.XXX STABLE. So here we
    #       ignore the non-promoted case because sbd_amount  asserts proper input units.
    promoted = sbd_amount(post['promoted']) if post['promoted'] != '0.000 HIVE' else None

    # convert to internal object
    row = None
    try:
        row = post_to_internal(post, core['id'], 'insert', promoted=promoted)
        row = dict(row)
    except Exception as e:
        log.error("post_to_internal: %s %s", repr(e), traceback.format_exc())
        raise e

    # normalized response
    ret = None
    try:
        if 'promoted' not in row: row['promoted'] = 0
        row['author_rep'] = author['reputation']
        ret = _bridge_post_object(row)
    except Exception as e:
        log.error("post_to_internal: %s %s", repr(e), traceback.format_exc())
        raise e

    # decorate
    if core['community_id']:
        sql = """SELECT title FROM hive_communities WHERE id = :id"""
        title = await db.query_one(sql, id=core['community_id'])

        sql = """SELECT role_id, title
                   FROM hive_roles
                  WHERE community_id = :cid
                    AND account_id = :aid"""
        role = await db.query_row(sql, cid=core['community_id'], aid=author['id'])

        ret['community_title'] = title
        ret['author_role'] = ROLES[role[0] if role else 0]
        ret['author_title'] = role[1] if role else ''

    return ret

import logging
from hive.db.adapter import Db

log = logging.getLogger(__name__)
DB = Db.instance()

def escape_characters(text):
    characters = ["'", "_", "%"]
    ret = str(text)
    for ch in characters:
        ret = ret.replace(ch, "\\" + ch)
    return ret

class PostDataCache(object):
    """ Procides cache for DB operations on post data table in order to speed up initial sync """
    _data = {}

    @classmethod
    def is_cached(cls, pid):
        """ Check if data is cached """
        return pid in cls._data

    @classmethod
    def add_data(cls, pid, post_data):
        """ Add data to cache """
        cls._data[pid] = post_data

    @classmethod
    def flush(cls):
        """ Flush data from cache to db """
        if cls._data:
            sql = """
                INSERT INTO 
                    hive_post_data (id, title, preview, img_url, body, json) 
                VALUES 
            """
            values = []
            for k, data in cls._data.items():
                title = "''" if not data['title'] else "'{}'".format(escape_characters(data['title']))
                preview = "''" if not data['preview'] else "'{}'".format(escape_characters(data['preview']))
                img_url = "''" if not data['img_url'] else "'{}'".format(escape_characters(data['img_url']))
                body = "''" if not data['body'] else "'{}'".format(escape_characters(data['body']))
                json = "'{}'" if not data['json'] else "'{}'".format(escape_characters(data['json']))
                values.append("({},{},{},{},{},{})".format(k, title, preview, img_url, body, json))
            sql += ','.join(values)
            sql += """
                ON CONFLICT (id)
                    DO
                        UPDATE SET 
                            title = EXCLUDED.title,
                            preview = EXCLUDED.preview,
                            img_url = EXCLUDED.img_url,
                            body = EXCLUDED.body,
                            json = EXCLUDED.json
                        WHERE
                            hive_post_data.id = EXCLUDED.id
            """
            DB.query(sql)
            cls._data.clear()

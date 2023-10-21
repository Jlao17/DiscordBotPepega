from sqlite3 import OperationalError

from helpers.db_connectv2 import startsql as sql
import logging

log = logging.getLogger(__name__)


async def check_key_in_db(game_id, shop, user_cnf=None):
    shop = shop.lower()
    try:
        await sql.execute("SELECT 1 FROM {} LIMIT 1".format(shop))
        exists = True
    except OperationalError as e:
        message = e.args[0]
        if message.startswith("No such table exists"):
            log.warning("Table {} does not exist".format(shop))
            exists = False
        else:
            raise

    if user_cnf:
        if exists:
            if user_cnf[1] == "eu":
                search = await sql.fetchall("SELECT * FROM {0} WHERE ID = {1} AND NOT REGION = 'na'".format(shop, game_id))
            elif user_cnf[1] == "na":
                search = await sql.fetchall("SELECT * FROM {0} WHERE ID = {1} AND NOT REGION = 'eu'".format(shop, game_id))
            else:
                search = await sql.fetchall("SELECT * FROM {0} WHERE ID = {1} AND REGION = '{2}'".format(shop, game_id, user_cnf[1]))
            if search:
                log.info("Found keys in DB - {}".format(shop))
                return search
            if not search:
                log.info("Found no key in DB - {}".format(shop))
                return None
    else:
        if exists:
            search = await sql.fetchall("SELECT * FROM {0} WHERE ID = {1}".format(shop, game_id))
            if search:
                log.info("Found keys in DB - {}".format(shop))
                return search
            if not search:
                log.info("Found no key in DB - {}".format(shop))
                return None


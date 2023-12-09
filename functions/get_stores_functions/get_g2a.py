import requests
from functions.filter_keys import filter_key, filter_g2a
from functions.check_key_in_db import check_key_in_db
import time
from helpers.db_connectv2 import startsql as sql
import logging

log = logging.getLogger(__name__)

browser_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
}


async def get_g2a(game_name, app_name, game_id, args, store, user_cnf):


    price_list = []
    # Convert steam id to our id (we swapped id's in database for g2a)
    game_id = await sql.fetchone("SELECT steam_id FROM steamdb WHERE id = %s", str(game_id))
    # Same principle as check for 1st update steamdb
    result = await check_key_in_db(game_id[0], store, user_cnf)

    if result is None:
        log.info("no result g2a")
        return price_list

    elif len(result) > 0:
        log.info("result > 0 g2a")
        return list(result)

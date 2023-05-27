from functions.filter_keys import filter_key
from functions.check_key_in_db import check_key_in_db
import time
from helpers.db_connectv2 import startsql as sql
import pandas as pd
import re
import logging
log = logging.getLogger(__name__)


async def get_eneba(game_name, app_name, game_id, args, store, user_cnf):
    price_list = []

    async def csv_parse(name, counter):
        df = pd.read_csv('eneba_csv.csv', skipinitialspace=True)
        df_dict = df.to_dict(orient='records')
        log.info(df_dict)
        for game in df_dict:
            if game['region'] != 'europe':
                continue

            offer_url = game['link']
            offer_price = game['price'].replace('EUR', '')
            offer_name = game['title']

            if offer_url is None or offer_price is None:
                continue
            filter_result = filter_key(offer_name, name, offer_url, offer_price)

            if filter_result is not None:
                price_list.append(filter_result)
                await sql.execute(
                    "INSERT INTO eneba (id, key_name, eneba_id, url, price, last_modified) VALUES "
                    "(%s, %s, %s, %s, %s, %s)",
                    (game_id, offer_name, game["id"], "{}".format(offer_url),
                     offer_price, time.time()))
                counter += 1
            else:
                continue

        return counter

    result = await check_key_in_db(game_id, store)
    if result is None:
        log.info("Searching for keys on Eneba store...")
        count = 0
        try:
            count = await csv_parse(game_name, count)
        except KeyError as e:
            log.exception(f'caught {type(e)}: e')
            return
        if count == 0:
            count = await csv_parse(app_name, count)
        if count == 0:
            count = await csv_parse(args["name"], count)
        # If it's still 0, use alternative names
        # args
        #
        #
        #
        print(args)

        return price_list

    elif len(result) > 0:
        for entry in result:
            if int(time.time()) - int(entry[4]) > 43200:
                log.info("Longer than 12 hours")
                # game_data, app_name = get_steam_game(result[2])
                # Upload the new data in db here:
                # update_steamdb_game(game_data, result[2])
                return list(result)

            else:
                log.info("Less than 12 hours")
                return list(result)

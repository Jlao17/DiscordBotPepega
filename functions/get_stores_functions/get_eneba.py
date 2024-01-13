from functions.filter_keys import filter_key
from functions.check_key_in_db import check_key_in_db
from functions.deprecated_functions.get_feed import get_eneba_csv
from helpers.db_connectv2 import startsql as sql
import pandas as pd
import logging
import time
log = logging.getLogger(__name__)


async def get_eneba(game_name, game_id, args, store, user_cnf):
    price_list = []

    async def csv_parse(name, counter):
        df = pd.read_csv('eneba_csv.csv', skipinitialspace=True)
        df_dict = df.to_dict(orient='records')
        for game in df_dict:
            # if game['region'] != 'europe':
            #     continue
            if game['region'] in ["united_states", "europe", "united_states"]:
                offer_url = game['link']
                offer_price = game['price'].replace('EUR', '')
                offer_name = game['title']
                offer_region = game['region']
                if offer_region == "united_states":
                    offer_region = "na"
                if offer_region == "europe":
                    offer_region = "eu"

                if offer_url is None or offer_price is None:
                    continue
                filter_result = filter_key(offer_name, name, offer_url, offer_price)

                if filter_result is not None:
                    regions_check = {"global": ["global"], "eu": ["eu", "global"], "na": ["na", "global"]}
                    if str(offer_region) in regions_check[str(user_cnf[1])]:
                        price_list.append(filter_result)
                    # Prevents duplicate keys in DB because of how region filtering works
                    # global keys in DB but no na keys -> don't insert global keys again
                    found = await sql.fetchone("SELECT * FROM eneba WHERE key_name = %s", offer_name)
                    if not found:
                        await sql.execute(
                            "INSERT INTO eneba (id, key_name, eneba_id, url, price, last_modified, region) VALUES "
                            "(%s, %s, %s, %s, %s, %s, %s)",
                            (game_id, offer_name, game["id"], "{}".format(offer_url),
                             offer_price, time.time(), offer_region))
                    counter += 1
                else:
                    continue
            else:
                continue
        return counter

    async def update_eneba_db(name, db_result):
        df = pd.read_csv('eneba_csv.csv', skipinitialspace=True)
        df_dict = df.to_dict(orient='records')
        for game in df_dict:
            for entry in db_result:
                db_key_name = entry[1]
                try:
                    if game["title"] == db_key_name:
                        # if game['region'] != 'europe':
                        #     continue
                        if game['region'] in ["united_states", "europe", "united_states"]:
                            offer_url = game['link']
                            offer_price = game['price'].replace('EUR', '')
                            offer_name = game['title']
                            offer_region = game['region']
                            if offer_region == "united_states":
                                offer_region = "na"
                            if offer_region == "europe":
                                offer_region = "eu"

                            if offer_url is None or offer_price is None:
                                continue
                            filter_result = filter_key(offer_name, name, offer_url, offer_price)

                            if filter_result is not None:
                                regions_check = {"global": ["global"], "eu": ["eu", "global"], "na": ["na", "global"]}
                                if str(offer_region) in regions_check[str(user_cnf[1])]:
                                    price_list.append(filter_result)
                                    await sql.execute(
                                        "UPDATE eneba "
                                        "SET id = %s, key_name = %s, eneba_id = %s, url = %s, price = %s, "
                                        "last_modified = %s "
                                        "WHERE key_name = %s",
                                        (game_id, offer_name, game["id"], "{}".format(offer_url),
                                         offer_price, time.time(), db_key_name))
                            else:
                                continue
                        else:
                            continue
                except KeyError:
                    log.info("Eneba warning - Price variable doesn't exist for {}".format(game["title"]))
        log.info("done update Eneba db")

    result = await check_key_in_db(game_id, store, user_cnf)
    if result is None:
        log.info("Searching for keys on Eneba store...")
        count = 0
        try:
            count = await csv_parse(game_name, count)
        except KeyError as e:
            log.exception(f'caught {type(e)}: e')
            return price_list
        if count == 0:
            await csv_parse(args["name"], count)
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
                count = 0
                try:
                    count = await update_eneba_db(game_name, result)

                    if count == 0:
                        await update_eneba_db(args["name"], result)
                except KeyError as e:
                    log.exception(f'caught {type(e)}: e')
                    return
                updated_result = await check_key_in_db(game_id, store, user_cnf)
                return list(updated_result)

            else:
                log.info("Less than 12 hours")
                return list(result)

    # elif len(result) > 0:
    #     for entry in result:
    #         if int(time.time()) - int(entry[4]) > 43200:
    #             log.info("Longer than 12 hours")
    #             try:
    #                 name_query = [game_name, app_name, args["name"]]  # specify the request names in the desired order
    #
    #                 for name in name_query:
    #                     json = json_request(name)
    #                     if await filtered_game_counter(json) > 0:
    #                         break
    #                     else:
    #                         continue
    #             except KeyError:
    #                 log.exception(KeyError)
    #                 return price_list
    #             await update_k4g_db(json, result)
    #             updated_result = await check_key_in_db(game_id, store, user_cnf)
    #             # game_data, app_name = get_steam_game(result[2])
    #             # Upload the new data in db here:
    #             # update_steamdb_game(game_data, result[2])
    #             return list(updated_result)
    #
    #     log.info("Less than 12 hours")
    #     return list(result)
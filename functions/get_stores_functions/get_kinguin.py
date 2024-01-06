import requests
from functions.filter_keys import filter_key
from functions.check_key_in_db import check_key_in_db
import time
from helpers.db_connectv2 import startsql as sql
from bot import config
import logging

log = logging.getLogger(__name__)

browser_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
}


async def get_kinguin(game_name, app_name, game_id, args, store, user_cnf):
    price_list = []

    async def json_request(name):
        # Kinguin doesn't allow you to use multiple regions at the same time
        url = "https://gateway.kinguin.net/esa/api/v1/products"

        querystring = {"name": name,
                       "regionId": "1",
                       "platform": "Epic Games, Steam, Other, EA Origin, Uplay, Battle.net, GOG COM, Bethesda, "
                                   "Rockstar Games, Mog Station"}
        querystring2 = {"name": name,
                       "regionId": "2",
                       "platform": "Epic Games, Steam, Other, EA Origin, Uplay, Battle.net, GOG COM, Bethesda, "
                                   "Rockstar Games, Mog Station"}
        querystring3 = {"name": name,
                       "regionId": "3",
                       "platform": "Epic Games, Steam, Other, EA Origin, Uplay, Battle.net, GOG COM, Bethesda, "
                                   "Rockstar Games, Mog Station"}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
            "X-Api-Key": config["kinguin_api"]
        }

        json1 = requests.request("GET", url, headers=headers, params=querystring).json()
        json2 = requests.request("GET", url, headers=headers, params=querystring2).json()
        json3 = requests.request("GET", url, headers=headers, params=querystring3).json()

        # Merge the "results" from both responses
        merged_results = json1["results"] + json2["results"] + json3["results"]

        # Create a new dictionary with the merged results and the item_count
        merged_response = {
            "results": merged_results,
        }
        log.info(merged_response)
        return merged_response

    async def json_parse(name, counter):
        json = await json_request(name)
        for offer in json["results"]:
            offer_url = "https://www.kinguin.net/category/" + \
                              str(offer["kinguinId"]) + "/" + \
                              offer["name"].replace(" ", "-")
            try:
                if offer["price"] is not None:
                    offer_price = str(f"{offer['price']}")  # + "EUR"
                    offer_name = offer["name"]
                    regions = {"3": "global", "1": "eu", "2": "na", "18": "na"}
                    offer_region = regions[str(offer["regionId"])]

                    filter_result = filter_key(offer_name, name, "{}?r=56785867".format(offer_url), offer_price)
                    if filter_result is not None:
                        regions_check = {"global": ["global"], "eu": ["eu", "global"], "na": ["na", "global"]}
                        if regions[str(offer["regionId"])] in regions_check[str(user_cnf[1])]:
                            log.info("Appended key {}, {}".format(offer_name, regions[str(offer["regionId"])]))
                            price_list.append(filter_result)
                        # Prevents duplicate keys in DB because of how region filtering works
                        # global keys in DB but no na keys -> don't insert global keys again
                        found = await sql.fetchone("SELECT * FROM kinguin WHERE key_name = %s", offer_name)
                        if not found:
                            await sql.execute(
                                "INSERT INTO kinguin (id, key_name, kinguin_id, url, price, last_modified, region) "
                                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                (game_id, offer_name, offer["productId"], "{}?r=56785867".format(offer_url),
                                 offer_price, time.time(), offer_region))
                        counter += 1
                    else:
                        continue
                else:
                    continue
            except KeyError:
                log.info("Kinguin warning - Price variable doesn't exist for {}".format(offer_url))
        return counter

    async def update_kinguin_db(db_json, db_result):
        for offer in db_json["results"]:
            for entry in db_result:
                db_key_name = entry[1]
                try:
                    if offer["name"] == db_key_name:
                        offer_url = "https://www.kinguin.net/category/" + \
                                    str(offer["kinguinId"]) + "/" + \
                                    offer["name"].replace(" ", "-")
                        if offer["price"] is not None:
                            offer_price = str(f"{offer['price']}")  # + "EUR"
                            offer_name = offer["name"]

                            filter_result = filter_key(offer_name, name, "{}?r=56785867".format(offer_url), offer_price)
                            if filter_result is not None:
                                price_list.append(filter_result)
                                log.info("start update kinguin db")
                                await sql.execute(
                                    "UPDATE kinguin "
                                    "SET id = %s, key_name = %s, kinguin_id = %s, url = %s, price = %s,"
                                    "   last_modified = %s "
                                    "WHERE key_name = %s ",
                                    (game_id, offer_name, offer["productId"], "{}?r=56785867".format(offer_url),
                             offer_price, time.time(), db_key_name))
                                log.info("done update kinguin db")
                            else:
                                continue
                        else:
                            continue
                    else:
                        continue
                except KeyError:
                    log.info("Kinguin warning - Price variable doesn't exist for {}".format(offer_url))
            log.info("done update Kinguin db")

    async def filtered_game_counter(db_json):
        filtered_count = 0
        for offer in db_json["results"]:
            offer_url = "https://www.kinguin.net/category/" + \
                        str(offer["kinguinId"]) + "/" + \
                        offer["name"].replace(" ", "-")
            if offer["price"] is not None:
                offer_price = str(f"{offer['price']}")  # + "EUR"
                offer_name = offer["name"]

                filter_result = filter_key(offer_name, name, "{}?r=56785867".format(offer_url), offer_price)
                if filter_result is not None:
                    filtered_count += 1

        return filtered_count

    result = await check_key_in_db(game_id, store, user_cnf)
    if result is None:
        log.info("Searching for keys on Kinguin store...")
        count = 0
        try:
            count = await json_parse(game_name, count)
        except KeyError:
            log.exception(KeyError)
            return price_list
        if count == 0:
            count = await json_parse(app_name, count)
        if count == 0:
            count = await json_parse(args["name"], count)
        # If it's still 0, use alternative names
        # args
        #
        #
        #
        return price_list

    elif len(result) > 0:
        if int(time.time()) - int(result[0][4]) > 43200:
            try:
                name_query = [game_name, app_name, args["name"]]  # specify the request names in the desired order

                for name in name_query:
                    json = await json_request(name)
                    if await filtered_game_counter(json) > 0:
                        break
                    else:
                        continue
            except KeyError:
                log.exception(KeyError)
                return
            await update_kinguin_db(json, result)
            updated_result = await check_key_in_db(game_id, store, user_cnf)
            log.info("Longer than 12 hours")
            # game_data, app_name = get_steam_game(result[2])
            # Upload the new data in db here:
            # update_steamdb_game(game_data, result[2])
            return list(updated_result)

        else:
            log.info("Less than 12 hours")
            return list(result)

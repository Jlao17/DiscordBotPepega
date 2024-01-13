import requests
from functions.filter_keys import filter_key
from functions.check_key_in_db import check_key_in_db
import time
from helpers.db_connectv2 import startsql as sql
import logging
import asyncio

log = logging.getLogger(__name__)

browser_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
}


async def get_k4g(game_name, game_id, args, store, user_cnf):
    price_list = []

    def json_request(name):
        import requests
        url = "https://k4g.com/api/v1/en/search/search"

        querystring = {"category_id": "2",
                       "product_type[]": ["1", "4"],
                       "platform[]": ["1", "10", "94", "2", "3", "4", "5", "12", "15", "16"],
                       "q": "{}".format(name.replace(" ", "+")),
                       "region[]": ["1", "2", "8"]
                       }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
        }

        game_json = (requests.request("GET", url, headers=headers, params=querystring))

        game_json = game_json.json()

        return game_json

    async def json_parse(name, counter):
        json = json_request(name)
        for offer in json["items"]:
            # print("REGION ->", str(offer["region"]["id"]), str(offer["region"]["name"]))
            offer_url = "https://k4g.com/product/" + "-" + offer["slug"] + "-" + str(offer["id"])
            try:
                if offer["featured_offer"] is not None:
                    offer_price = str(offer["featured_offer"]["price"]["EUR"]["price"])  # + "EUR"
                    offer_name = offer["title"]
                    filter_result = filter_key(offer_name, name, "{}?r=pricewatch".format(offer_url), offer_price)
                    if filter_result is not None:
                        # This checks and appends the keys if from the correct region -> then shown to the user
                        regions = {"1": "global", "2": "eu", "8": "na", "50": "eu", "51": "global"}
                        regions_check = {"global": ["global"], "eu": ["eu", "global"], "na": ["na", "global"]}
                        if regions[str(offer["region"]["id"])] in regions_check[str(user_cnf[1])]:
                            price_list.append(filter_result)
                        # Prevents duplicate keys in DB because of how region filtering works
                        # global keys in DB but no na keys -> don't insert global keys again
                        found = await sql.fetchone("SELECT * FROM k4g WHERE key_name = %s", offer_name)
                        if not found:
                            await sql.execute(
                                "INSERT INTO k4g (id, key_name, k4g_id, url, price, last_modified, region) VALUES "
                                "(%s, %s, %s, %s, %s, %s, %s)",
                                (game_id, offer_name, offer["id"], "{}?r=pricewatch".format(offer_url),
                                 offer_price, time.time(), regions[str(offer["region"]["id"])]))
                        counter += 1
                    else:
                        continue
                else:
                    continue
            except KeyError:
                log.info("K4G warning - Price variable doesn't exist for {}".format(offer["title"]))
        return counter

    async def update_k4g_db(db_json, db_result):
        for offer in db_json["items"]:
            for entry in db_result:
                db_key_name = entry[1]
                try:
                    if offer["title"] == db_key_name:
                        offer_url = "https://k4g.com/product/" + "-" + offer["slug"] + "-" + str(offer["id"])
                        if offer["featured_offer"] is not None:
                            offer_price = str(offer["featured_offer"]["price"]["EUR"]["price"])  # + "EUR"
                            offer_name = offer["title"]
                            filter_result = filter_key(offer_name, name, "{}?r=pricewatch".format(offer_url),
                                                       offer_price)
                            if filter_result is not None:
                                price_list.append(filter_result)
                                log.info("start update k4g db")
                                await sql.execute(
                                    "UPDATE k4g "
                                    "SET id = %s, key_name = %s, k4g_id = %s, url = %s, price = %s,"
                                    "   last_modified = %s "
                                    "WHERE key_name = %s ",
                                    (game_id, offer_name, offer["id"], "{}?r=pricewatch".format(offer_url),
                                     offer_price, time.time(), db_key_name))
                            else:
                                continue
                        else:
                            continue
                    else:
                        continue
                except KeyError:
                    log.info("K4G warning - Price variable doesn't exist for {}".format(offer["title"]))
        log.info("done update K4G db")

    async def filtered_game_counter(db_json):
        filtered_count = 0
        for offer in db_json["items"]:
            offer_url = "https://k4g.com/product/" + "-" + offer["slug"] + "-" + str(offer["id"])
            if offer["featured_offer"] is not None:
                offer_price = str(offer["featured_offer"]["price"]["EUR"]["price"])  # + "EUR"
                offer_name = offer["title"]
                filter_result = filter_key(offer_name, name, "{}?r=pricewatch".format(offer_url), offer_price)
                if filter_result is not None:
                    filtered_count += 1

        return filtered_count

    result = await check_key_in_db(game_id, store, user_cnf)
    if result is None:
        count = 0
        try:
            count = await json_parse(game_name, count)

            if count == 0:
                await json_parse(args["name"], count)
        except KeyError:
            log.exception(KeyError)
            return
        # If it's still 0, use alternative names
        # args
        #
        #
        #

        return price_list

    elif len(result) > 0:
        for entry in result:
            if int(time.time()) - int(entry[4]) > 43200:
                log.info("Longer than 12 hours")
                try:
                    name_query = [game_name, args["name"]]  # specify the request names in the desired order

                    for name in name_query:
                        json = json_request(name)
                        if await filtered_game_counter(json) > 0:
                            break
                        else:
                            continue
                except KeyError:
                    log.exception(KeyError)
                    return price_list
                await update_k4g_db(json, result)
                updated_result = await check_key_in_db(game_id, store, user_cnf)
                # game_data, app_name = get_steam_game(result[2])
                # Upload the new data in db here:
                # update_steamdb_game(game_data, result[2])
                return list(updated_result)

        log.info("Less than 12 hours")
        return list(result)

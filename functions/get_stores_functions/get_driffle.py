import requests
from functions.filter_keys import filter_key
from functions.check_key_in_db import check_key_in_db
import time
from helpers.db_connectv2 import startsql as sql
import logging
from functions.currency_converter import todollar

log = logging.getLogger(__name__)

browser_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
}


async def get_driffle(game_name, app_name, game_id, args, store, user_cnf):
    price_list = []

    def json_request(name):
        import requests
        regions = {"global": "3", "eu": "3,1", "na": "3,2"}
        # Change region and game/dlc in the link, params won't work
        url = "https://search.driffle.com/products/v2/list?limit=10&productType=game&region={}&page=1&q={}&worksOn[]=windows".format(regions[user_cnf[1]], name.replace(" ", "+"))
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
        }

        game_json = requests.request("GET", url, headers=headers).json()

        print(game_json)
        return game_json

    async def json_parse(name, counter):
        json = json_request(name)
        for offer in json["data"]:
            offer_url = "https://driffle.com/" + offer["slug"]
            try:
                if offer["price"] is not None:
                    offer_price = str(offer["price"])  # + "EUR"
                    offer_name = offer["title"]
                    filter_result = filter_key(offer_name, name, "{}".format(offer_url), offer_price)
                    if filter_result is not None:
                        regions = {"3": "global", "1": "eu", "2": "na"}
                        price_list.append(filter_result)
                        found = await sql.fetchone("SELECT * FROM driffle WHERE key_name = %s", offer_name)
                        if not found:
                            await sql.execute(
                                "INSERT INTO driffle (id, key_name, url, price, last_modified, region) VALUES "
                                "(%s, %s, %s, %s, %s, %s)",
                                (game_id, offer_name, "{}".format(offer_url),
                                 offer_price, time.time(), regions[str(offer["regionId"])]))  # user_cnf[1]))
                        counter += 1
                    else:
                        continue
                else:
                    continue
            except KeyError:
                log.info("Driffle warning - Price variable doesn't exist for {}".format(offer["title"]))
        return counter

    async def update_driffle_db(db_json, db_result):
        log.info("start update driffle db")
        for offer in db_json["data"]:
            for entry in db_result:
                db_key_name = entry[1]
                try:
                    if offer["title"] == db_key_name:
                        offer_url = "https://driffle.com/" + "-" + offer["slug"]
                        if offer["price"] is not None:
                            offer_price = str(offer["price"])  # + "EUR"
                            offer_name = offer["title"]
                            filter_result = filter_key(offer_name, name, "{}".format(offer_url), offer_price)
                            if filter_result is not None:
                                price_list.append(filter_result)
                                await sql.execute(
                                    "UPDATE driffle "
                                    "SET id = %s, key_name = %s, url = %s, price = %s,"
                                    "   last_modified = %s "
                                    "WHERE key_name = %s ",
                                    (game_id, offer_name, "{}".format(offer_url),
                                     offer_price, time.time(), db_key_name))
                            else:
                                continue
                        else:
                            continue
                    else:
                        continue
                except KeyError:
                    log.info("Driffle warning - Price variable doesn't exist for {}".format(offer["title"]))
        log.info("done update driffle db")

    async def filtered_game_counter(db_json):
        filtered_count = 0
        for offer in db_json["data"]:
            offer_url = "https://driffle.com/" + offer["slug"]
            if offer["price"] is not None:
                offer_price = str(offer["price"])  # + "EUR"
                offer_name = offer["title"]
                filter_result = filter_key(offer_name, name, "{}".format(offer_url), offer_price)
                if filter_result is not None:
                    filtered_count += 1

        return filtered_count

    result = await check_key_in_db(game_id, store, user_cnf)
    if result is None:
        count = 0
        try:
            count = await json_parse(game_name, count)

            if count == 0:
                count = await json_parse(app_name, count)
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
        for timestamp in result:
            if int(time.time()) - int(timestamp[4]) > 43200:
                log.info("Longer than 12 hours")
                try:
                    name_query = [game_name, app_name, args["name"]]  # specify the request names in the desired order

                    for name in name_query:
                        json = json_request(name)
                        if await filtered_game_counter(json) > 0:
                            break
                        else:
                            continue
                except KeyError:
                    log.exception(KeyError)
                    return price_list
                print("JSON", json)
                await update_driffle_db(json, result)
                updated_result = await check_key_in_db(game_id, store)
                # game_data, app_name = get_steam_game(result[2])
                # Upload the new data in db here:
                # update_steamdb_game(game_data, result[2])
                return list(updated_result)
            else:
                continue

        else:
            log.info("Less than 12 hours")
            return list(result)

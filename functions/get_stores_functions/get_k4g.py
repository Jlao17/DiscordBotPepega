import requests
from functions.filter_keys import filter_key
from functions.check_key_in_db import check_key_in_db
import time
from helpers.db_connectv2 import startsql as sql
import logging

log = logging.getLogger(__name__)

browser_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
}


async def get_k4g(game_name, app_name, game_id, args, store, user_cnf):
    price_list = []

    def json_request(name):
        import requests
        regions = {"global": ["1"], "eu": ["1", "2"], "na": ["1", "6"]}
        url = "https://k4g.com/api/v1/en/search/search"

        querystring = {"category_id": "2",
                       "product_type[]": ["1", "4"],
                       "platform[]": ["1", "10", "94", "2", "3", "4", "5", "12", "15", "16"],
                       "q": "{}".format(name.replace(" ", "+")),
                       # "region[]": regions[user_cnf[1]]
                       }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
        }

        game_json = requests.request("GET", url, headers=headers, params=querystring).json()

        return game_json

    async def json_parse(name, counter):
        json = json_request(name)
        for offer in json["items"]:
            offer_url = "https://k4g.com/product/" + "-" + offer["slug"] + "-" + str(offer["id"])
            if offer["featured_offer"] is not None:
                offer_price = str(offer["featured_offer"]["price"]["EUR"]["price"])  # + "EUR"
                offer_name = offer["title"]
                filter_result = filter_key(offer_name, name, "{}?r=pricewatch".format(offer_url), offer_price)
                if filter_result is not None:
                    price_list.append(filter_result)
                    await sql.execute(
                        "INSERT INTO k4g (id, key_name, k4g_id, url, price, last_modified, region) VALUES "
                        "(%s, %s, %s, %s, %s, %s, %s)",
                        (game_id, offer_name, offer["id"], "{}?r=pricewatch".format(offer_url),
                         offer_price, time.time(), "EUR"
                         # user_cnf[1]
                         )
                    )
                    counter += 1
                else:
                    continue
            else:
                continue
        return counter

    async def update_k4g_db(db_json, db_result):
        for offer in db_json["items"]:
            for entry in db_result:
                db_key_name = entry[1]
                if offer["title"] == db_key_name:
                    offer_url = "https://k4g.com/product/" + "-" + offer["slug"] + "-" + str(offer["id"])
                    if offer["featured_offer"] is not None:
                        offer_price = str(offer["featured_offer"]["price"]["EUR"]["price"])  # + "EUR"
                        offer_name = offer["title"]
                        filter_result = filter_key(offer_name, name, "{}?r=pricewatch".format(offer_url), offer_price)
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
                            log.info("done update k4g db")
                        else:
                            continue
                    else:
                        continue
                else:
                    continue

    async def filtered_game_counter(db_json):
        filtered_count = 0
        for offer in db_json["items"]:
            offer_url = "https://k4g.com/product/" + "-" + offer["slug"] + "-" + str(offer["id"])
            if offer["featured_offer"] is not None:
                offer_price = str(offer["featured_offer"]["price"]["EUR"]["price"])  # + "EUR"
                offer_name = offer["title"]
                filter_result = filter_key(offer_name, name, "{}?r=pricewatch".format(offer_url), offer_price)
                if filter_result is not None:
                    filtered_count += 1;

        return filtered_count

    result = await check_key_in_db(game_id, store)
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
        if int(time.time()) - int(result[0][4]) > 43200:
            log.info("Longer than 12 hours")
            try:
                name_query = [game_name, app_name, args["name"]]  # specify the request names in the desired order

                for name in name_query:
                    json = json_request(name)
                    if filtered_game_counter(json) > 0:
                        break
                    else:
                        continue
            except KeyError:
                log.exception(KeyError)
                return price_list
            await update_k4g_db(json, result)
            updated_result = await check_key_in_db(game_id, store)
            # game_data, app_name = get_steam_game(result[2])
            # Upload the new data in db here:
            # update_steamdb_game(game_data, result[2])
            return list(updated_result)

        else:
            log.info("Less than 12 hours")
            return list(result)

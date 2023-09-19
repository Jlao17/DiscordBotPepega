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
    async def json_request(name):
        import requests

        url = "https://www.g2a.com/search/api/v2/products"

        querystring = {"itemsPerPage": "18",
                       "include[0]": "filters",
                       "currency": "EUR",
                       "isWholesale": "false",
                       "f[product-kind][0]": "10",
                       "f[product-kind][1]": "8",
                       "f[device][0]": "1118",
                       "f[regions][0]": "8355",
                       "category": "189",
                       "phrase": name}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
        }

        game_json = requests.request("GET", url, headers=headers, params=querystring).json()

        return game_json

    async def json_parse(name, counter):
        print(1)
        json = await json_request(name)
        print(2)
        log.info(json)
        print(3)
        for offer in json["data"]["items"]:
            try:
                print(4)
                offer_url = "https://www.g2a.com" + offer["href"]
                offer_price = offer["price"]  # + g2a_app["currency"]
                offer_name = offer["name"]
                # Delete key is price or link is non-existing
                if offer_url is None or offer_price is None:
                    log.info("offer rejected")
                    continue
                else:
                    # if filter_g2a(offer_name, name):
                    filter_result = filter_key(offer_name, name, "{}?gtag=9b358ba6b1"
                                               .format(offer_url), offer_price)
                    if filter_result is not None:
                        price_list.append(filter_result)
                        await sql.execute(
                            "INSERT INTO g2a (id, key_name, g2a_id, url, price, last_modified) VALUES "
                            "(%s, %s, %s, %s, %s, %s)",
                            (game_id, offer_name, offer["id"], "{}?gtag=9b358ba6b1".format(offer_url),
                             offer_price, time.time()))
                        counter += 1
                    else:
                        continue
                    # else:
                    #     print("offer deleted")
                    #     continue
            except KeyError:
                continue

        return counter

    async def update_g2a_db(db_json, db_result):
        for offer in db_json["data"]["items"]:
            for entry in db_result:
                db_key_name = entry[1]
                if offer["name"] == db_key_name:
                    offer_url = "https://www.g2a.com" + offer["href"]
                    offer_price = offer["price"]  # + g2a_app["currency"]
                    offer_name = offer["name"]
                    if offer_url is None or offer_price is None:
                        continue
                    else:
                        filter_result = filter_key(offer_name, name, "{}?gtag=9b358ba6b1"
                                                   .format(offer_url), offer_price)
                        if filter_result is not None:
                            price_list.append(filter_result)
                            log.info("start update g2a db")
                            await sql.execute(
                                "UPDATE g2a "
                                "SET id = %s, key_name = %s, g2a_id = %s, url = %s, price = %s,"
                                "   last_modified = %s "
                                "WHERE key_name = %s ",
                                (game_id, offer_name, offer["id"], "{}?gtag=9b358ba6b1".format(offer_url),
                                 offer_price, time.time(), db_key_name))
                            log.info("done update g2a db")
                        else:
                            continue
                else:
                    continue

    async def filtered_game_counter(db_json):
        filtered_count = 0
        for offer in db_json["data"]["items"]:
            try:
                offer_url = "https://www.g2a.com" + offer["href"]
                offer_price = offer["price"]  # + g2a_app["currency"]
                offer_name = offer["name"]
                if offer_url is None or offer_price is None:
                    continue
                else:
                    filter_result = filter_key(offer_name, name, "{}?gtag=9b358ba6b1"
                                               .format(offer_url), offer_price)
                if filter_result is not None:
                    filtered_count += 1
            except KeyError:
                pass

        return filtered_count

    price_list = []
    # Same principle as check for 1st update steamdb
    result = await check_key_in_db(game_id, store)
    if result is None:
        print(101)
        count = 0
        print(202)
        try:
            print(303)
            count = await json_parse(game_name, count)
            print(404)
            if count == 0:
                count = await json_parse(app_name, count)
            # Try using IGDB game name instead
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
                return price_list
            await update_g2a_db(json, result)
            updated_result = await check_key_in_db(game_id, store)
            log.info("Longer than 12 hours")
            # game_data, app_name = get_steam_game(result[2])
            # Upload the new data in db here:
            # update_steamdb_game(game_data, result[2])
            return list(updated_result)

        else:
            log.info("Less than 12 hours")
            return list(result)









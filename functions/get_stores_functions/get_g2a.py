import requests
from functions.filter_keys import filter_key, filter_g2a
from functions.check_key_in_db import check_key_in_db
import time
from helpers.db_connectv2 import startsql as sql

browser_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
}


async def get_g2a(game_name, app_name, game_id, args, store):
    def json_request(name):
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
        }

        game_json = requests.request("GET", url, headers=headers, params=querystring).json()

        return game_json

    async def json_parse(name, counter):
        json = json_request(name)
        for offer in json["data"]["items"]:
            offer_url = "https://www.g2a.com" + offer["href"]
            offer_price = offer["price"]  # + g2a_app["currency"]
            offer_name = offer["name"]
            # Delete key is price or link is non-existing
            if offer_url is None or offer_price is None:
                continue
            else:
                if filter_g2a(offer_name, name):
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
                else:
                    continue
        return counter

    price_list = []
    # Same principle as check for 1st update steamdb
    result = await check_key_in_db(game_id, store)
    if result is None:
        count = 0
        try:
            count = await json_parse(game_name, count)
        except KeyError:
            print('KeyError in G2A' + KeyError)
            return price_list
        if count == 0:
            count = await json_parse(app_name, count)
        # Try using IGDB game name instead
        if count == 0:
            count = await json_parse(args["name"], count)
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
                print("Longer than 12 hours")
                # game_data, app_name = get_steam_game(result[2])
                # Upload the new data in db here:
                # update_steamdb_game(game_data, result[2])
                return list(result)

            else:
                print("Less than 12 hours")
                return list(result)

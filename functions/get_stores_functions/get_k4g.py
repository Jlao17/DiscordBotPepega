import requests
from functions.filter_keys import filter_key
from functions.check_key_in_db import check_key_in_db
import time
from helpers.db_connectv2 import startsql as sql

browser_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
}


async def get_k4g(game_name, app_name, game_id, args, store):
    print(game_name, app_name)
    price_list = []

    def json_request(name):
        import requests

        url = "https://k4g.com/api/v1/en/search/search"

        querystring = {"category_id": "2",
                       "platform[]": ["1", "10", "94", "2", "3", "4", "5", "12", "15", "16"],
                       "q": "{}".format(name.replace(" ", "+")),
                       "region[]": ["1", "2", "6"]}

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
                filter_result = filter_key(offer_name, name, offer_url, offer_price)
                if filter_result is not None:
                    price_list.append(filter_result)
                    await sql.execute(
                        "INSERT INTO k4g (id, key_name, k4g_id, url, price, last_modified) VALUES "
                        "(%s, %s, %s, %s, %s, %s)",
                        (game_id, offer_name, offer["id"], "{}?r=pricewatch".format(offer_url),
                         offer_price, time.time()))
                    counter += 1
                else:
                    continue
            else:
                continue
        return counter

    result = await check_key_in_db(game_id, store)
    if result is None:
        count = 0
        try:
            count = await json_parse(game_name, count)
        except KeyError:
            print('KeyError in k4g' + KeyError)
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

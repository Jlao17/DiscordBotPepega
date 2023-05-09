import requests
from functions.filter_keys import filter_key
from functions.check_key_in_db import check_key_in_db
import time
from helpers.db_connectv2 import startsql as sql

browser_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
}


async def get_k4g(game_name, app_name, game_id, args):
    print(game_name)
    price_list = []

    def json_request(name):
        import requests

        url = "https://k4g.com/api/v1/en/search/search"

        querystring = {"category_id": "2",
                       "platform[]": ["1", "2", "3", "4", "10", "12"],
                       "product_type[]": "1",
                       "q": "{}".format(name.replace(" ", "+")),
                       "regions[]": "1"}

        payload = ""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
        }

        game_json = requests.request("GET", url, data=payload, headers=headers, params=querystring).json()

        return game_json

    result = await check_key_in_db(game_id, "k4g")

    if result is None:
        count = 0
        game_json_k4g = json_request(game_name)
        try:
            for k4g_app in game_json_k4g["items"]:
                k4g_app_url = "https://k4g.com/product/" + "-" + k4g_app["slug"] + "-" + str(k4g_app["id"])
                if k4g_app["featured_offer"] is not None:
                    k4g_app_price = str(k4g_app["featured_offer"]["price"]["EUR"]["price"])  # + "EUR"
                    k4g_app_name = k4g_app["title"]
                    filter_result = filter_key(k4g_app_name, game_name, k4g_app_url, k4g_app_price)
                    if filter_result is not None:
                        price_list.append(filter_result)
                        await sql.execute(
                            "INSERT INTO k4g (id, key_name, k4g_id, url, price, last_modified) VALUES "
                            "(%s, %s, %s, %s, %s, %s)",
                            (game_id, k4g_app_name, k4g_app["id"], "{}?r=pricewatch".format(k4g_app_url),
                             k4g_app_price, time.time()))
                        count += 1
                else:
                    continue
        except KeyError:
            print('KeyError in k4g' + KeyError)
            return
        if count == 0:
            app_json_k4g = json_request(app_name)
            for k4g_app in app_json_k4g["items"]:
                k4g_app_url = "https://k4g.com/product/" + "-" + k4g_app["slug"] + "-" + str(k4g_app["id"])
                if k4g_app["featured_offer"] is not None:
                    k4g_app_price = str(k4g_app["featured_offer"]["price"]["EUR"]["price"])  # + "EUR"
                    k4g_app_name = k4g_app["title"]
                    filter_result = filter_key(k4g_app_name, game_name, k4g_app_url, k4g_app_price)
                    if filter_result is not None:
                        price_list.append(filter_result)
                        await sql.execute(
                            "INSERT INTO k4g (id, key_name, k4g_id, url, price, last_modified) VALUES "
                            "(%s, %s, %s, %s, %s, %s)",
                            (game_id, k4g_app_name, k4g_app["id"], "{}?r=pricewatch".format(k4g_app_url),
                             k4g_app_price, time.time()))
                        count += 1
        if count == 0:
            app_json_k4g = json_request(args["name"])
            for k4g_app in app_json_k4g["items"]:
                k4g_app_url = "https://k4g.com/product/" + "-" + k4g_app["slug"] + "-" + str(k4g_app["id"])
                if k4g_app["featured_offer"] is not None:
                    k4g_app_price = str(k4g_app["featured_offer"]["price"]["EUR"]["price"])  # + "EUR"
                    k4g_app_name = k4g_app["title"]
                    filter_result = filter_key(k4g_app_name, args["name"], k4g_app_url, k4g_app_price)
                    if filter_result is not None:
                        price_list.append(filter_result)
                        await sql.execute(
                            "INSERT INTO k4g (id, key_name, k4g_id, url, price, last_modified) VALUES "
                            "(%s, %s, %s, %s, %s, %s)",
                            (game_id, k4g_app_name, k4g_app["id"], "{}?r=pricewatch".format(k4g_app_url),
                             k4g_app_price, time.time()))
                        count += 1
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

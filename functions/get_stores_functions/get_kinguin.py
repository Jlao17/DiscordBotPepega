import requests
from functions.filter_keys import filter_key
from functions.check_key_in_db import check_key_in_db
import time
from helpers.db_connectv2 import startsql as sql
from bot import config

browser_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
}


async def get_kinguin(game_name, app_name, game_id, args):
    price_list = []

    # def json_request(name):
    #     game_json = requests.get(
    #         "https://www.kinguin.net/services/library/api/v1/products/search?platforms=2,1,5,6,3,15,22,24,18,4,23&"
    #         "productType=1&"
    #         "countries=NL&"  # NL,US
    #         "systems=Windows&"
    #         "languages=en_US&"
    #         "active=1&"
    #         "hideUnavailable=0&"
    #         "phrase=" + name + "&"
    #                            "page=0&"
    #                            "size=50&"
    #                            "sort=bestseller.total,DESC&"
    #                            "visible=1&"
    #                            "lang=en_US&"
    #                            "store=kinguin", headers=browser_headers
    #     ).json()
    #
    #     return game_json

    def json_request(name):
        url = "https://gateway.kinguin.net/esa/api/v1/products"

        querystring = {"name": name,
                       "regionId": "3",
                       "platform": "Epic Games, Steam, Other, EA Origin, Uplay, Battle.net, GOG COM, Bethesda, "
                                   "Rockstar Games, Mog Station"}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
            "X-Api-Key": config["kinguin_api"]
        }

        game_json = requests.request("GET", url, headers=headers, params=querystring).json()

        return game_json

    async def json_parse(name, counter):
        json = json_request(name)
        for offer in json["results"]:
            offer_url = "https://www.kinguin.net/category/" + \
                              str(offer["kinguinId"]) + "/" + \
                              offer["name"].replace(" ", "-")
            if offer["price"] is not None:
                offer_price = str(f"{offer['price']}")  # + "EUR"
                offer_name = offer["name"]

                filter_result = filter_key(offer_name, name, offer_url, offer_price)
                if filter_result is not None:
                    price_list.append(filter_result)
                    await sql.execute(
                        "INSERT INTO kinguin (id, key_name, kinguin_id, url, price, last_modified) VALUES "
                        "(%s, %s, %s, %s, %s, %s)",
                        (game_id, offer_name, offer["productId"], "{}".format(offer_url),
                         offer_price, time.time()))
                    counter += 1
                else:
                    continue
            else:
                continue
        return counter

    result = await check_key_in_db(game_id, "kinguin")
    if result is None:
        print("Searching for keys on Kinguin store...")
        count = 0
        try:
            count = await json_parse(game_name, count)
        except KeyError:
            print('KeyError in Kinguin' + KeyError)
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

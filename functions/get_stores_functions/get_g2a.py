import requests
from functions.filter_keys import filter_key, filter_g2a
from functions.check_key_in_db import check_key_in_db
import time
from helpers.db_connectv2 import startsql as sql

browser_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
}


async def get_g2a(game_name, app_name, game_id):
    def json_request(name):
        game_json = requests.get(
            "https://www.g2a.com/search/api/v2/products?itemsPerPage=18&include[0]=filters&"
            "currency=EUR&isWholesale=false&f[product-kind][0]=10&f[product-kind][1]=8&f[device][0]=1118&"
            "f[regions][0]=8355&category=189&phrase=" + name, headers=browser_headers
        ).json()

        return game_json

    price_list = []
    # Same principle as check for 1st update steamdb
    result = await check_key_in_db(game_id, "g2a")

    if result is None:
        count = 0
        game_json_g2a = json_request(game_name)
        try:
            for g2a_app in game_json_g2a["data"]["items"]:
                g2a_app_url = "https://www.g2a.com" + g2a_app["href"]
                g2a_app_price = g2a_app["price"]  # + g2a_app["currency"]
                g2a_app_name = g2a_app["name"]
                if filter_g2a(g2a_app_name, game_name):
                    filter_result = filter_key(g2a_app_name, game_name, "{}?gtag=9b358ba6b1".format(g2a_app_url),
                                               g2a_app_price)
                    if filter_result is not None:
                        price_list.append(filter_result)
                        await sql.execute("INSERT INTO g2a (id, key_name, url, price, last_modified, g2a_id) VALUES "
                                          "(%s, %s, %s, %s, %s, %s)",
                                          (game_id, g2a_app_name, "{}?gtag=9b358ba6b1".format(g2a_app_url),
                                           g2a_app_price, int(time.time()), g2a_app["id"]))
                        count += 1
                else:
                    continue
        except KeyError:
            print('KeyError in G2A' + KeyError)
            return
        if count == 0:
            app_json_g2a = json_request(app_name)
            for g2a_app in app_json_g2a["data"]["items"]:
                g2a_app_url = "https://www.g2a.com" + g2a_app["href"]
                g2a_app_price = g2a_app["price"]  # + g2a_app["currency"]
                g2a_app_name = g2a_app["name"]
                # Delete key is price or link is non-existing
                if g2a_app_url is None or g2a_app_price is None:
                    continue
                else:
                    if filter_g2a(g2a_app_name, game_name):
                        filter_result = filter_key(g2a_app_name, game_name, "{}?gtag=9b358ba6b1"
                                                   .format(g2a_app_url), g2a_app_price)
                        if filter_result is not None:
                            price_list.append(filter_result)
                            await sql.execute(
                                "INSERT INTO G2A (id, key_name, g2a_id, url, price, last_modified) VALUES "
                                "(%s, %s, %s, %s, %s, %s)",
                                (game_id, g2a_app_name, g2a_app["id"], "{}?gtag=9b358ba6b1".format(g2a_app_url),
                                 g2a_app_price, time.time()))
        return price_list
    elif len(result) > 0:
        for entry in result:
            if int(time.time()) - int(entry[4]) > 43200:
                print("Longer than 12 hours")
                # game_data, app_name = get_steam_game(result[2])
                # Upload the new data in db here:
                # update_steamdb_game(game_data, result[2])
                return None

            else:
                print("Less than 12 hours")
                return list(result)

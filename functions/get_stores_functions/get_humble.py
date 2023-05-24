import requests
from bs4 import BeautifulSoup
from functions.filter_keys import filter_key, filter_g2a
from functions.check_key_in_db import check_key_in_db
import time
from helpers.db_connectv2 import startsql as sql
import logging

log = logging.getLogger(__name__)

browser_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
}


async def get_g2a(game_name, app_name, game_id, args, store):
    def json_request(name):
        import requests

        url = "https://www.humblebundle.com/store/api/search?"

        querystring = {"sort": "bestselling",
                       "filter": "all",
                       "search": name,
                       "request": "1"}

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
        }

        game_json = requests.request("GET", url, headers=headers, params=querystring).json()

        return game_json

    price_list = []
    # Same principle as check for 1st update steamdb
    result = await check_key_in_db(game_id, store)

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
            log.exception(KeyError)
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
                                "INSERT INTO g2a (id, key_name, g2a_id, url, price, last_modified) VALUES "
                                "(%s, %s, %s, %s, %s, %s)",
                                (game_id, g2a_app_name, g2a_app["id"], "{}?gtag=9b358ba6b1".format(g2a_app_url),
                                 g2a_app_price, time.time()))
                            count += 1
        # Try using IGDB game name instead
        if count == 0:
            app_json_g2a = json_request(args["name"])
            for g2a_app in app_json_g2a["data"]["items"]:
                g2a_app_url = "https://www.g2a.com" + g2a_app["href"]
                g2a_app_price = g2a_app["price"]  # + g2a_app["currency"]
                g2a_app_name = g2a_app["name"]
                # Delete key is price or link is non-existing
                if g2a_app_url is None or g2a_app_price is None:
                    continue
                else:
                    if filter_g2a(g2a_app_name, args["name"]):
                        filter_result = filter_key(g2a_app_name, args["name"], "{}?gtag=9b358ba6b1"
                                                   .format(g2a_app_url), g2a_app_price)
                        if filter_result is not None:
                            price_list.append(filter_result)
                            await sql.execute(
                                "INSERT INTO g2a (id, key_name, g2a_id, url, price, last_modified) VALUES "
                                "(%s, %s, %s, %s, %s, %s)",
                                (game_id, g2a_app_name, g2a_app["id"], "{}?gtag=9b358ba6b1".format(g2a_app_url),
                                 g2a_app_price, time.time()))
                            count += 1
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
                # game_data, app_name = get_steam_game(result[2])
                # Upload the new data in db here:
                # update_steamdb_game(game_data, result[2])
                return list(result)

            else:
                log.info("Less than 12 hours")
                return list(result)

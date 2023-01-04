import requests
from functions.filter_keys import filter_key
from functions.get_steam_price import get_steam_price
import discord

browser_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
}


def g2a(steam_game):
    game_appid, game_name, game_data, app_name = steam_game
    price_list = []
    print(1)

    def json_request(name):
        game_json = requests.get(
            "https://www.g2a.com/search/api/v2/products?itemsPerPage=18&include[0]=filters&"
            "currency=EUR&isWholesale=false&f[product-kind][0]=10&f[product-kind][1]=8&f[device][0]=1118&"
            "f[regions][0]=8355&category=189&phrase=" + name, headers=browser_headers
        ).json()
        return game_json

    count = 0
    game_json_g2a = json_request(game_name)
    app_json_g2a = json_request(app_name)

    for g2a_app in game_json_g2a["data"]["items"]:
        g2a_app_url = "https://www.g2a.com" + g2a_app["href"]
        g2a_app_price = g2a_app["price"] + g2a_app["currency"]
        g2a_app_name = g2a_app["name"]
        price_list.append(filter_key(g2a_app_name, game_name, "{}?gtag=9b358ba6b1".format(g2a_app_url),
                                     g2a_app_price))
        count += 1
    if count == 0:
        for g2a_app in app_json_g2a["data"]["items"]:
            g2a_app_url = "https://www.g2a.com" + g2a_app["href"]
            g2a_app_price = g2a_app["price"] + g2a_app["currency"]
            g2a_app_name = g2a_app["name"]
            price_list.append(filter_key(g2a_app_name, game_name, "{}?gtag=9b358ba6b1".format(g2a_app_url),
                                         g2a_app_price))

    return price_list, game_data, game_appid


def kinguin(steam_game):
    pass


def k4g(steam_game):
    print(11)
    game_appid, game_name, game_data, app_name = steam_game
    price_list = []

    def json_request(name):
        game_json = requests.get(
            "https://k4g.com/api/v1/en/search/search?category_id=2&"
            "platform[]=1&"
            "platform[]=2&"
            "platform[]=3&"
            "platform[]=4&"
            "platform[]=10&"
            "platform[]=12&"
            "product_type[]=1&"
            "q={}&region[]=1".format(name.replace(" ", "+")), headers=browser_headers
        ).json()
        return game_json

    count = 0
    game_json_k4g = json_request(game_name)
    app_json_k4g = json_request(app_name)

    for k4g_app in game_json_k4g["items"]:
        k4g_app_url = "https://k4g.com/product/" + "-" + k4g_app["slug"] + "-" + str(k4g_app["id"] +
                                                                                     "?r=pricewatch")
        if k4g_app["featured_offer"] is not None:
            k4g_app_price = str(k4g_app["featured_offer"]["price"]["EUR"]["price"]) + "EUR"
            k4g_app_name = k4g_app["title"]
            price_list.append(filter_key(k4g_app_name, app_name, "{}?r=pricewatch".format(k4g_app_url),
                                         k4g_app_price))
            count += 1

    if count == 0:
        for k4g_app in app_json_k4g["items"]:
            k4g_app_url = "https://k4g.com/product/" + "-" + k4g_app["slug"] + "-" + str(k4g_app["id"] +
                                                                                         "?r=pricewatch")
            print(1)
            if k4g_app["featured_offer"] is not None:
                k4g_app_price = str(k4g_app["featured_offer"]["price"]["EUR"]["price"]) + "EUR"
                k4g_app_name = k4g_app["title"]
                price_list.append(filter_key(k4g_app_name, app_name, "{}?r=pricewatch".format(k4g_app_url),
                                             k4g_app_price))
    price_list = list(filter(lambda item: item is not None, price_list))
    return price_list, game_data, game_appid


def gamivo(steam_game):
    pass

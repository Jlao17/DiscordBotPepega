import requests
from functions.filter_keys import filter_key
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

    return price_list


def kinguin(steam_game):
    pass


def k4g(steam_game):
    pass


def gamivo(steam_game):
    pass


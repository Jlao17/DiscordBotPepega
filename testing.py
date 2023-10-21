import requests
import time


def get_steam_game3(args):
    game_appid = args
    game_json_steam = requests.get(
        "http://store.steampowered.com/api/appdetails?appids=" + game_appid + "&l=english&currency=3").json()
    if game_json_steam[game_appid]["success"]:
        game_data = game_json_steam[game_appid]["data"]
        print("ROMENIA", game_data["price_overview"])
        app_name = game_data["name"]
        return game_data, app_name
    else:
        return None, None


def get_steam_game2(args):
    game_appid = args
    game_json_steam = requests.get(
        "http://store.steampowered.com/api/appdetails?appids=" + game_appid + "&l=english&currency=2").json()
    if game_json_steam[game_appid]["success"]:
        game_data = game_json_steam[game_appid]["data"]
        print("BRIISH", game_data["price_overview"])
        app_name = game_data["name"]
        return game_data, app_name
    else:
        return None, None


def get_steam_game1(args):
    game_appid = args
    proxies = {
        'http': 'http://47.88.62.42:80',
        # 'https': 'https://207.244.228.76:8128',
    }
    cookies = {
        "ak_bmsc": "89F5CF316F6449BDE1DD5AFB37BFA067~000000000000000000000000000000~YAAQnnzRF+qwHR+LAQAAA8+fUxX2glxH2828OiLEZ/3BRDfqvkXake55Tq3tiQoQ42pvtCrmO7VNAZD2BdefUf+SluAqVocU3FbqIXEJQBsNXIp8KtpDBM6mpqnj+6RK4JbvMvWCAlBFRhhN1fB3Q5vP3n9xnyRj5tPMeFV8nTlctROaa5qJmbCKS6ebDXK2zgK5+ek7FPTAcMhox6gQ1aNmYxHn7LuMQIqg1Fg5IezM5QlQOMLjTLwLHMC3tx66g8kV3xQvkt1XZHUcB0MWB08VetSQk0c6z4I9WwdbxZ9FyKf0ZPZ7CU4wkKJb9YEgEx1jSnRXudeBefAyT/PeVcUCrYw2XS9C8Hu5WWQKMTjxEVjkrdzheEVk6NBysiafBR2F4PlA",
        "app_impressions": "2573690@1_5_9__405|2557420@1_5_9__405|2557410@1_5_9__405|2557400@1_5_9__405|2557390@1_5_9__405|2161370@1_5_9__405|1172380@1_5_9__412|1774580@1_5_9__412|2161370@1_5_9__405|1172380@1_5_9__412|1774580@1_5_9__412",
        "browserid": "3029292636980560605",
        "recentapps": '{"1774580":1697915097,"2440510":1697914836}',
        "sessionid": "15280b0fb845c263625ae316",
        "steamCountry": "US|abf3554e394579374c036206f4b0c3d9"
        }

    game_json_steam = requests.get(
        "http://store.steampowered.com/api/appdetails?appids=" + game_appid + "&l=english&currency=1", proxies=proxies,
        cookies=cookies
    ).json()
    if game_json_steam[game_appid]["success"]:
        game_data = game_json_steam[game_appid]["data"]
        print("USD", game_data["price_overview"])
        app_name = game_data["name"]
        return game_data, app_name
    else:
        return None, None


(get_steam_game1(str(2440510)))
time.sleep(5)
(get_steam_game2(str(2440510)))
time.sleep(5)
(get_steam_game3(str(2440510)))

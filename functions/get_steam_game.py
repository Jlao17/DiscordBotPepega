import requests


def get_steam_game(args, user_cnf):
    cclist = {"euro": "de", "dollar": "us", "pound": "gb"}
    currency = cclist[user_cnf[2]]
    game_appid = args
    game_json_steam = requests.get(
        "http://store.steampowered.com/api/appdetails?appids=" + game_appid + "&l=english&cc=" + currency
    ).json()
    if game_json_steam[game_appid]["success"]:
        game_data = game_json_steam[game_appid]["data"]
        app_name = game_data["name"]
        return game_data, app_name
    else:
        return None, None






import requests


def get_steam_game(args):
    game_appid = args
    game_json_steam = requests.get(
        "http://store.steampowered.com/api/appdetails?appids=" + game_appid + "&l=english&&currency=3"
    ).json()
    if game_json_steam[game_appid]["success"]:
        game_data = game_json_steam[game_appid]["data"]
        app_name = game_data["name"]
        return game_data, app_name
    else:
        return None, None




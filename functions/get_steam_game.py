from functions.normalized_text import normalized_text
import requests


def get_steam_game(steam_apps, args):
    game_appid = None
    print("args: " + args)
    for app in steam_apps["applist"]["apps"]:
        if normalized_text(app["name"].lower()) == normalized_text(args.lower()):
            print("found it")
            game_appid = str(app["appid"])
            print("appid:" + game_appid)
            break
    if game_appid is None:
        print("game not found")
        return

    game_json_steam = requests.get(
        "http://store.steampowered.com/api/appdetails?appids=" + game_appid + "&l=english&&currency=3"
    ).json()
    print(("http://store.steampowered.com/api/appdetails?appids=" + game_appid + "&l=english&&currency=3"))
    game_data = game_json_steam[game_appid]["data"]
    game_name = game_data["name"]
    return game_appid, game_name, game_data

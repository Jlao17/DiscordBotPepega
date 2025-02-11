from functions.normalized_text import normalized_text
import requests


def check_game_exists(steam_apps, data):
    game_list = []
    for game in data:
        game_list.append(normalized_text(game["name"]))
    # Remove duplicates
    # game_list = list(dict.fromkeys(game_list))

    # Check steam first before passing list
    # updated_game_list = []
    # for app in steam_apps["applist"]["apps"]:
    #     if normalized_text(app["name"].lower()) in game_list:
    #         updated_game_list.append(app["name"])
    # updated_game_list = list(set(updated_game_list))

    game_list = list(set(game_list))
    # print(updated_game_list)
    # return updated_game_list
    return game_list


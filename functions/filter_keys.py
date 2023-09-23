from functions.deprecated_functions.check_base_game import check_base_game,check_base_game_nodlc
import re


def filter_key(key_name, game_name, key_url, key_price):
    if key_name.lower().startswith(game_name.lower()) \
            and re.search(r'\b' + game_name.lower() + r'\b', key_name.lower()) \
            and check_base_game(game_name.lower(), key_name.lower()):
        return [game_name, key_name, key_url, key_price]


# No DLC check (eg for Driffle)
def filter_key_nodlc(key_name, game_name, key_url, key_price):
    if key_name.lower().startswith(game_name.lower()) \
            and re.search(r'\b' + game_name.lower() + r'\b', key_name.lower()) \
            and check_base_game_nodlc(game_name.lower(), key_name.lower()):
        return [game_name, key_name, key_url, key_price]


def filter_g2a(key_name, game_name):
    game_list = game_name.split()
    for game_word in game_list:
        if re.search(game_word, key_name):
            continue
        else:
            return False
    return True

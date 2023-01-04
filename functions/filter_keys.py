from functions.check_base_game import check_base_game
import re


def filter_key(key_name, game_name, key_url, key_price):
    if key_name.lower().startswith(game_name.lower()) \
            and re.search(r'\b' + game_name.lower() + r'\b', key_name.lower()) \
            and check_base_game(game_name.lower(), key_name.lower()):
        return [game_name, key_name, key_url, key_price]

import re


def check_base_game(game_name, vendor_name):
    trigger_words = ["remake", "remade", "remaster", "remastered", "dlc"]
    # Check if one of the trigger words is present in the search argument or in the vendor name
    for word in trigger_words:
        if re.search(r'\b' + word + r'\b', game_name):
            for word2 in trigger_words:
                if re.search(r'\b' + word2 + r'\b', vendor_name):
                    return True
            return True
        elif re.search(r'\b' + word + r'\b', game_name):
            return False
        else:
            for word3 in trigger_words:
                if re.search(r'\b' + word3 + r'\b', vendor_name):
                    return False
    return True

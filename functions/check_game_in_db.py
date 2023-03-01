from functions.normalized_text import normalized_text
import requests
from helpers.db_connect import startsql as sql


def check_game_in_db(args):
    if isinstance(args, int):
        search = sql.fetchone("SELECT * FROM steamdb_test WHERE steam_id = %s", (str(args),))
        if search is not None:
            print("Found game in DB")
            return search
        else:
            print("Found game not in DB")
            return None
    else:
        search = sql.fetchone("SELECT * FROM steamdb_test WHERE NAME = %s", (args["name"],))
        if search is not None:
            print("Found game in DB")
            return search
        else:
            for alt_name in args["alternative_names"]:
                search = sql.fetchone("SELECT * FROM steamdb_test WHERE NAME = %s", (alt_name["name"],))
                if search is not None:
                    print("Found game in DB")
                    return search
                else:
                    continue
        if search is None:
            print("Found game not in DB")
            return None



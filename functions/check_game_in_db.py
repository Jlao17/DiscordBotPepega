from functions.normalized_text import normalized_text
import requests
from helpers.db_connectv2 import startsql as sql


async def check_game_in_db(args):
    if isinstance(args, int):
        search = await sql.fetchone("SELECT * FROM steamdb_test WHERE steam_id = %s", (str(args)))
        if search is not None:
            print("Found game in steamdb")
            return search
        else:
            print("Found no game in steamdb")
            return None
    else:
        search = await sql.fetchone("SELECT * FROM steamdb_test WHERE NAME = %s", (args["name"],))
        print(search)
        if search is not None:
            print("Found game in steamdb")
            return search
        else:
            if hasattr(args, "alternative_names"):
                for alt_name in args["alternative_names"]:
                    search = await sql.fetchone("SELECT * FROM steamdb_test WHERE NAME = %s", (alt_name["name"],))
                    if search is not None:
                        print("Found game in steamdb")
                        return search
                    else:
                        continue
            else:
                return None
        if search is None:
            print("Found no game in steamdb")
            return None



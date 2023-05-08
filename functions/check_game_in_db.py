from helpers.db_connectv2 import startsql as sql


async def check_game_in_db(args):
    """Check if this is a link, if not then use the steam uid provided by IGDB.
    If that doesn't work, use the old school compare name method"""
    if isinstance(args, int):
        search = await sql.fetchone("SELECT * FROM steamdb_test WHERE steam_id = %s", (str(args)))
        if search is not None:
            print("Found game in steamdb")
            return search
        else:
            print("Found no game in steamdb")
            return None
    else:
        for uid in args["external_games"]:
            if uid["category"] == 1:
                search = await sql.fetchone("SELECT * FROM steamdb_test WHERE steam_id = %s", (uid["uid"],))
                if search is None:
                    search = await sql.fetchone("SELECT * FROM steamdb_test WHERE NAME = %s", (args["name"],))
                    if search is not None:
                        print("Found game in steamdb")
                        return search
                    else:
                        if "alternative_names" in args:
                            for alt_name in args["alternative_names"]:
                                print(alt_name)
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
                else:
                    print("Found game in steamdb")
                    return search


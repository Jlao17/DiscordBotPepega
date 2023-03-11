from helpers.db_connectv2 import startsql as sql


async def check_key_in_db(id, shop):
    print(4)
    if shop == "g2a":
        print(5)
        search = await sql.fetchone("SELECT * FROM g2a WHERE ID = %s", id)
        print(6)
        if search is not None:
            print("Found keys in DB")
            return search
        if search is None:
            print("Found key not in DB")
            return None
    elif shop == "k4g":
        search = await sql.fetchone("SELECT * FROM k4g WHERE ID = %s", id)
        print(5)
        if search is not None:
            print("Found keys in DB")
            return search
        if search is None:
            print("Found key not in DB")
            return None
    elif shop == "kinguin":
        search = await sql.fetchone("SELECT * FROM kinguin WHERE ID = %s", id)
        print(5)
        if search is not None:
            print("Found keys in DB")
            return search
        if search is None:
            print("Found key not in DB")
            return None
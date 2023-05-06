from helpers.db_connectv2 import startsql as sql


async def check_key_in_db(id, shop):
    print(4)
    if shop == "g2a":
        print(5)
        search = await sql.fetchall("SELECT * FROM g2a WHERE ID = %s", id)
        print(6)
        print(search)
        if search:
            print("Found keys in DB g2a")
            return search
        if not search:
            print("Found key not in DB g2a")
            return None
    elif shop == "k4g":
        search = await sql.fetchall("SELECT * FROM k4g WHERE ID = %s", id)
        print(5)
        if search:
            print("Found keys in DB k4g")
            return search
        if not search:
            print("Found key not in DB k4g")
            return None
    elif shop == "kinguin":
        search = await sql.fetchall("SELECT * FROM kinguin WHERE ID = %s", id)
        print(5)
        if search:
            print("Found keys in DB kinguin")
            return search
        if not search:
            print("Found key not in DB kinguin")
            return None

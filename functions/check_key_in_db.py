from helpers.db_connectv2 import startsql as sql


async def check_key_in_db(id, shop):
    if shop == "g2a":
        search = await sql.fetchall("SELECT * FROM g2a WHERE ID = %s", id)
        if search:
            print("Found keys in DB - G2A")
            return search
        if not search:
            print("Found no key in DB - G2A")
            return None
    elif shop == "k4g":
        search = await sql.fetchall("SELECT * FROM k4g WHERE ID = %s", id)
        if search:
            print("Found keys in DB - K4G")
            return search
        if not search:
            print("Found no key in DB - K4G")
            return None
    elif shop == "kinguin":
        search = await sql.fetchall("SELECT * FROM kinguin WHERE ID = %s", id)
        if search:
            print("Found keys in DB - Kinguin")
            return search
        if not search:
            print("Found no key in DB - Kinguin")
            return None
    elif shop == "eneba":
        search = await sql.fetchall("SELECT * FROM eneba WHERE ID = %s", id)
        if search:
            print("Found keys in DB - Eneba")
            return search
        if not search:
            print("Found no key in DB - Eneba")
            return None

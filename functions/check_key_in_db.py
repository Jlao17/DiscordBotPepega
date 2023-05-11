from sqlite3 import OperationalError

from helpers.db_connectv2 import startsql as sql


async def check_key_in_db(game_id, shop):
    shop = shop.lower()
    try:
        await sql.execute("SELECT 1 FROM {} LIMIT 1".format(shop))
        exists = True
    except OperationalError as e:
        message = e.args[0]
        if message.startswith("No such table exists"):
            print("Table {} does not exist".format(shop))
            exists = False
        else:
            raise

    if exists:
        search = await sql.fetchall("SELECT * FROM {0} WHERE ID = {1}".format(shop, game_id))
        if search:
            print("Found keys in DB - {}".format(shop))
            return search
        if not search:
            print("Found no key in DB - {}".format(shop))
            return None


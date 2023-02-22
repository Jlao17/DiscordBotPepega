from helpers.db_connect import startsql as sql


def update_steamdb_game(game_data, result):
    if "price_overview" not in game_data:
        price_initial = "Free"
        price_final = "Free"
        price_discount = "Free"
    else:
        price_initial = game_data["price_overview"]["initial"]
        price_final = game_data["price_overview"]["final"]
        price_discount = game_data["price_overview"]["discount_percent"]
    unix = int(time.time())
    print(unix, price_initial, price_final, price_discount, game_data["type"])
    sql.execute("UPDATE steamdb_test SET thumbnail = %s, price_initial = %s, price_final = %s, "
                "discount = %s, type = %s, last_modified_search = %s WHERE steam_id = %s",
                (game_data["header_image"], price_initial, price_final, price_discount, game_data["type"],
                 unix, result))
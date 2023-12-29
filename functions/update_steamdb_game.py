from helpers.db_connectv2 import startsql as sql
import time
import requests


async def update_steamdb_game(game_data, result):
    # Get the price for EU
    game_json_steam = requests.get(
        "http://store.steampowered.com/api/appdetails?appids=" + result + "&l=english&cc=de"
    ).json()
    if game_json_steam[result]["success"]:
        game_data = game_json_steam[result]["data"]
        if "price_overview" not in game_data:
            price_initial = "Free"
            price_final = "Free"
            price_discount = "Free"
        else:
            price_initial = game_data["price_overview"]["initial"]
            price_final = game_data["price_overview"]["final"]
            price_discount = game_data["price_overview"]["discount_percent"]


    # Get the price for US as well
    game_json_steam = requests.get(
        "http://store.steampowered.com/api/appdetails?appids=" + result + "&l=english&cc=us"
    ).json()
    if game_json_steam[result]["success"]:
        game_data = game_json_steam[result]["data"]
        if "price_overview" not in game_data:
            price_final = "Free"
        else:
            price_final_dollar = game_data["price_overview"]["final"]

    # Get the price for UK as well
    game_json_steam = requests.get(
        "http://store.steampowered.com/api/appdetails?appids=" + result + "&l=english&cc=gb"
    ).json()
    if game_json_steam[result]["success"]:
        game_data = game_json_steam[result]["data"]
        if "price_overview" not in game_data:
            price_final = "Free"
        else:
            price_final_pound = game_data["price_overview"]["final"]


    unix = int(time.time())
    await sql.execute("UPDATE steamdb SET thumbnail = %s, price_initial = %s, price_final = %s, "
                      "price_final_dollar = %s, price_final_pound = %s, "
                      "discount = %s, type = %s, last_modified_search = %s WHERE steam_id = %s",
                      (game_data["header_image"], price_initial, price_final, price_final_dollar,
                       price_final_pound, price_discount, game_data["type"], unix, result))
    return {"euro": price_final, "dollar": price_final_dollar, "pound": price_final_pound}

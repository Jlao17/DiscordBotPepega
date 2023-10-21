PRICE = 0
GAME_HEADER = 1


def get_steam_price(game_data, embed, game_appid, check=None):
    if check is None:
        if "price_overview" not in game_data:
            price_total = game_data["name"] + ": Free"
        else:
            price = game_data["price_overview"]
            price_currency = price["currency"]
            price_final = price["final"]
            if isinstance(price_final, int):
                price_total = f"€{(price_final / 100):.2f}"  # + price_currency
            # price_discount = price["discount_percent"]
        embed.set_thumbnail(url=game_data["header_image"])
    else:
        price_total = game_data[PRICE]
        if isinstance(game_data[PRICE], int):
            price_total = f"€{(int(game_data[PRICE]) / 100):.2f}"
        embed.set_thumbnail(url=game_data[GAME_HEADER])
    embed.add_field(
        name="Steam - " + price_total,
        value="[{name}]({url})".format(
            name="Steam Store",
            url="https://store.steampowered.com/app/{}/".format(game_appid)
        )
    )
    return embed


def get_steam_price_dollar(game_data, embed, game_appid, check=None):
    if check is None:
        if "price_overview" not in game_data:
            price_total_dollar = game_data["name"] + ": Free"
        else:
            price = game_data["price_overview"]
            # price_currency = price["currency"]
            price_final = price["final"]
            if isinstance(price_final, int):
                price_total_dollar = f"${(price_final / 100):.2f}"  # + price_currency
            # price_discount = price["discount_percent"]
        embed.set_thumbnail(url=game_data["header_image"])
    else:
        price_total = game_data[PRICE]
        price_total_dollar = price_total.replace("€", "$")
        if isinstance(game_data[PRICE], int):
            price_total_dollar = f"${(int(game_data[PRICE]) / 100):.2f}"
        embed.set_thumbnail(url=game_data[GAME_HEADER])
    embed.add_field(
        name="Steam - " + price_total_dollar,
        value="[{name}]({url})".format(
            name="Steam Store",
            url="https://store.steampowered.com/app/{}/".format(game_appid)
        )
    )
    return embed

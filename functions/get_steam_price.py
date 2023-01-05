def get_steam_price(game_data, embed, game_appid):
    if "price_overview" not in game_data:
        price_total = game_data["name"] + ": Free"
    else:
        price = game_data["price_overview"]
        price_currency = price["currency"]
        price_final = price["final"]
        price_total = "€" + str(price_final / 100)  # + price_currency
        # price_discount = price["discount_percent"]
    embed.add_field(
        name="Steam - " + price_total,
        value="[{name}]({url})".format(
            name="Steam Store",
            url="https://store.steampowered.com/app/{}/".format(game_appid)
        )
    )
    embed.set_thumbnail(url=game_data["header_image"])
    return embed

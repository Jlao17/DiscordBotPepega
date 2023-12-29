import discord
from functions.currency_converter import todollar, toeur, topound


async def list_to_embed(data, name, user_cnf):
    if data:
        prices_embed = discord.Embed(
            title="Price information {}".format(name),
            description=data[0][0],
            color=0x9C84EF
        )
        if len(data) > 1:
            for info in data[:10]:
                if user_cnf[2] == "dollar":
                    price = await todollar(info[3])
                elif user_cnf[2] == "euro":
                    price = await toeur(info[3])
                elif user_cnf[2] == "pound":
                    price = await topound(info[3])
                prices_embed.add_field(
                    name="{price}".format(price=price),
                    value="[{name}]({url})".format(name=info[1], url=info[2])
                )
        else:
            if user_cnf[2] == "dollar":
                price = await todollar(data[0][3])
            elif user_cnf[2] == "euro":
                price = await toeur(data[0][3])
            elif user_cnf[2] == "pound":
                price = await topound(data[0][3])
            prices_embed.add_field(
                name="{price}".format(price=price),
                value="[{name}]({url})".format(name=data[0][1], url=data[0][2])
            )
        return prices_embed
    else:
        return None

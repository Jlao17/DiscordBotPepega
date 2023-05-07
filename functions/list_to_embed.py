import discord


def list_to_embed(data, name):
    if data:
        prices_embed = discord.Embed(
            title="Price information {}".format(name),
            description=data[0][0],
            color=0x9C84EF
        )
        if len(data) > 1:
            for info in data:
                prices_embed.add_field(
                    name="€{price}".format(price=info[3]),
                    value="[{name}]({url})".format(name=info[1], url=info[2])
                )
        else:
            prices_embed.add_field(
                name="€{price}".format(price=data[0][3]),
                value="[{name}]({url})".format(name=data[0][1], url=data[0][2])
            )
        return prices_embed
    else:
        return None
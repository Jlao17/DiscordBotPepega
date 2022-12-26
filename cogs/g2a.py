import platform

import discord
import requests
import json
from discord.ext import commands
from discord.ext.commands import Context
from bot import config
from helpers.db_connect import startsql as sql


class g2a(commands.Cog, name="g2a"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="g2a",
        description="g2a",
    )
    async def g2a(self, context: Context):\

        client_id = config["g2a_client_id"]
        api_key = config["g2a_api"]
        headers = {
            "Authorization": client_id + ", " + api_key,
        }

        for x in range(1, 500):
            params = {
                "page": x
            }
            g2a_json = requests.get("https://api.g2a.com/v1/products", params=params, headers=headers).json()
            # print(json.dumps(g2a_json, indent=4))
            for y in range(len(g2a_json["docs"])):
                game = g2a_json["docs"][y]
                game_name = game["name"]
                game_id = game["id"]
                game_price = game["minPrice"]
                query = "INSERT INTO games (Name, g2a_id, g2a_price) VALUES (%s, %s, %s)"
                sql.execute(query, (game_name, game_id, game_price))



        # embed = discord.Embed(
        #     title=game_name,
        #     color=0x9C84EF
        # )
        # if len(game_info) > 6:
        #     for x in range(6):
        #         embed.add_field(
        #             name=game_info[x]["shop"]["name"] + " - " + game_currency + str(game_info[x]["price_new"]),
        #             value=game_info[x]["url"]
        #         )
        # else:
        #     for x in range(len(game_info)):
        #         embed.add_field(
        #             name=game_info[x]["shop"]["name"] + " - " + game_currency + str(game_info[x]["price_new"]),
        #             value=game_info[x]["url"]
        #         )
        #
        # await context.send(embed=embed)

        # embed = discord.Embed(
        #     title=game_name,
        #     description=f"{game_description}",
        #     color=0x9C84EF
        # )
        # embed.set_thumbnail(url=game_thumbnail)
        #
        # await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(g2a(bot))

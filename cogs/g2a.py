import platform

import discord
import requests
import json
from discord.ext import commands
from discord.ext.commands import Context
from bot import config


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
        print(client_id + ", " + api_key)
        headers = {
            "Authorization": client_id + ", " + api_key
        }


        g2a = requests.get("https://api.g2a.com/v1/products?page=1", headers=headers).json()
        print(g2a)

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

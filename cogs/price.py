import platform

import discord
import requests
import json
from discord.ext import commands
from discord.ext.commands import Context
from bot import config


class Price(commands.Cog, name="search"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="price",
        description="Get the price of a game",
    )
    async def price(self, context: Context, *, args: str):
        """
        Search and show the price of a game
        :param context: The hybrid command context.
        :param args: The game to get the price of.
        """

        args = args.lower()
        game_search = requests.get("https://api.isthereanydeal.com/v02/search/search/?key=" + config["itad_api"] +
                                   "&q=" + args).json()  # Search for the game based on the user defined `args`
        game_name = game_search["data"]["results"][0]["title"]  # Get the name of the game (best match for `args`)
        game_name_query = game_search["data"]["results"][0]["plain"]  # Get the plain name used for further querying
        game_info_query = requests.get("https://api.isthereanydeal.com/v01/game/prices/?key=" + config["itad_api"] +
                                       "&plains=" + game_name_query).json()  # Use `game_name_query` to find the price
        # of the game that
        game_info = game_info_query["data"][game_name_query]["list"]
        game_currency_query = game_info_query[".meta"]["currency"]

        if game_currency_query == "EUR":
            game_currency = "€"
        elif game_currency_query == "USD":
            game_currency = "$"

        embed = discord.Embed(
            title=game_name,
            color=0x9C84EF
        )
        if len(game_info) > 6:
            for x in range(6):
                embed.add_field(
                    name=game_info[x]["shop"]["name"] + " - " + game_currency + str(game_info[x]["price_new"]),
                    value=game_info[x]["url"]
                )
        else:
            for x in range(len(game_info)):
                embed.add_field(
                    name=game_info[x]["shop"]["name"] + " - " + game_currency + str(game_info[x]["price_new"]),
                    value=game_info[x]["url"]
                )

        await context.send(embed=embed)

        # embed = discord.Embed(
        #     title=game_name,
        #     description=f"{game_description}",
        #     color=0x9C84EF
        # )
        # embed.set_thumbnail(url=game_thumbnail)
        #
        # await context.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Price(bot))

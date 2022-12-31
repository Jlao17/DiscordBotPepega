import platform
import string
import discord
import requests
import json
from bot import config
from igdb.wrapper import IGDBWrapper
from discord.ext import commands
from discord.ui import View, Select
from functions.get_steam_price import get_steam_price
from functions.check_base_game import check_base_game
from functions.get_steam_game import get_steam_game
import re

asciiAndNumbers = string.ascii_letters + string.digits


class Kinguin(commands.Cog, name="kinguin"):
    def __init__(self, bot):
        self.bot = bot
        self.wrapper = IGDBWrapper(config["igdbclient"], config["igdbaccess"])
        self.steam_apps = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2").json()
        self.browser_headers = {  # Mimic Browser URL request
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
        }

    @commands.hybrid_command(
        name="kinguin",
        description="kinguin",
    )
    async def kinguin(self, ctx, *, args: str):
        """https://api-docs.igdb.com/#about"""
        byte_array = self.wrapper.api_request(
            'games',
            'fields name, alternative_names.*; limit 10; where category = (0,8,9); search "{}";'.format(args)
        )
        data = json.loads(byte_array)

        # Mimic browser API request

        def get_game(args):
            game_appid, game_name, game_data, app_name = get_steam_game(self.steam_apps, args)
            prices_embed = discord.Embed(
                title="Price information",
                description=args,
                color=0x9C84EF
            )

            def json_request(name):
                game_json = requests.get(
                    "https://www.kinguin.net/services/library/api/v1/products/search?platforms=2,1,5,6,3,15,22,24,18,4,23&"
                    "productType=1&"
                    "countries=NL,US&"
                    "systems=Windows&"
                    "languages=en_US&"
                    "active=1&"
                    "hideUnavailable=0&"
                    "phrase=" + name + "&"
                                       "page=0&"
                                       "size=50&"
                                       "sort=bestseller.total,DESC&"
                                       "visible=1&"
                                       "lang=en_US&"
                                       "store=kinguin", headers=self.browser_headers
                ).json()
                return game_json

            count = 0
            game_json_kinguin = json_request(game_name)
            app_json_kinguin = json_request(app_name)

            for kinguin_app in game_json_kinguin["_embedded"]["products"]:
                kinguin_app_url = "https://www.kinguin.net/category/" + \
                                  str(kinguin_app["externalId"]) + "/" + \
                                  kinguin_app["name"].replace(" ", "-")
                if kinguin_app["price"] is not None:
                    kinguin_app_price = str(kinguin_app["price"]["lowestOffer"] / 100) + "EUR"
                    kinguin_app_name = kinguin_app["name"]
                    embed_name = kinguin_app_name + " - " + kinguin_app_price

                    if kinguin_app_name.lower().startswith(game_name.lower()) \
                            and re.search(r'\b' + game_name.lower() + r'\b', kinguin_app_name.lower()) \
                            and check_base_game(game_name.lower(), kinguin_app_name.lower()):
                        prices_embed.add_field(
                            name="Kinguin - {price}".format(price=kinguin_app_price),
                            value="[{name}]({url})".format(name=embed_name, url=kinguin_app_url)
                        )
                        count += 1
            if count == 0:
                for kinguin_app in app_json_kinguin["_embedded"]["products"]:
                    kinguin_app_url = "https://www.kinguin.net/category/" + \
                                      str(kinguin_app["externalId"]) + "/" + \
                                      kinguin_app["name"].replace(" ", "-")
                    if kinguin_app["price"] is not None:
                        kinguin_app_price = str(kinguin_app["price"]["lowestOffer"] / 100) + "EUR"
                        kinguin_app_name = kinguin_app["name"]
                        embed_name = kinguin_app_name + " - " + kinguin_app_price

                        if kinguin_app_name.lower().startswith(app_name.lower()) \
                                and re.search(r'\b' + app_name.lower() + r'\b', kinguin_app_name.lower()) \
                                and check_base_game(app_name.lower(), kinguin_app_name.lower()):
                            prices_embed.add_field(
                                name="Kinguin - {price}".format(price=kinguin_app_price),
                                value="[{name}]({url})".format(name=embed_name, url=kinguin_app_url)
                            )

            get_steam_price(game_data, prices_embed, game_appid)
            return prices_embed

        async def print_game(choice, interaction=None):
            check_name = get_game(choice["name"])
            if check_name is None:
                for alt_name in choice["alternative_names"]:
                    check_name = get_game(alt_name["name"])
            if check_name is None:
                if interaction is None:
                    await ctx.send("Game could not be found on Steam.")
                else:
                    await interaction.response.send_message("Game could not be found on Steam.")
            else:
                if interaction is None:
                    await ctx.send(embed=check_name)
                else:
                    await interaction.response.send_message(embed=check_name)

        # Search results 0
        if len(data) < 1:
            await ctx.send("I've found no game")
        # Search results more than 1
        elif len(data) > 1:
            x = 1
            game_list = []
            for game in data:
                game_list.append(discord.SelectOption(label=game["name"], value="{}".format(x)))
                x += 1
            embed = discord.Embed(title="Select game", description="")
            select = Select(
                placeholder="Select a game",
                options=game_list
            )

            async def callback(interaction):
                for choice in range(0, 11):
                    if select.values[0] == str(choice):
                        choice_data = data[choice - 1]
                        async with ctx.typing():
                            await print_game(choice_data, interaction)

            select.callback = callback
            view = View()
            view.add_item(select)
            await ctx.send(embed=embed, view=view)
        # Search results one
        else:
            async with ctx.typing():
                await print_game(data[0])

        # Output price for that one game
        # To do:    1. dropdown list if more than one game in list
        #           2. Output prices for selected game


async def setup(bot):
    await bot.add_cog(Kinguin(bot))

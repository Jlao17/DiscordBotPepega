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


class k4g(commands.Cog, name="k4g"):
    def __init__(self, bot):
        self.bot = bot
        self.wrapper = IGDBWrapper(config["igdbclient"], config["igdbaccess"])
        self.steam_apps = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2").json()
        self.browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
        }

    @commands.hybrid_command(
        name="k4g",
        description="Search for games",
    )
    async def k4g(self, ctx, *, args: str):
        """https://api-docs.igdb.com/#about"""
        byte_array = self.wrapper.api_request(
            'games',
            'fields name, alternative_names.*; limit 10; where category = (0,8,9); search "{}";'.format(args)
        )
        data = json.loads(byte_array)
        # Mimic browser API request

        def get_game(args):
            game_appid, game_name, game_data = get_steam_game(self.steam_apps, args)
            prices_embed = discord.Embed(
                title="Price information",
                description=args,
                color=0x9C84EF
            )


            #G2A
            game_json_g2a = requests.get(
                "https://k4g.com/api/v1/en/search/search?category_id=2&"
                "platform[]=1&"
                "platform[]=2&"
                "platform[]=3&"
                "platform[]=4&"
                "platform[]=10&"
                "platform[]=12&"
                "product_type[]=1&"
                "q={}&region[]=1".format(game_name.replace(" ", "+")), headers=self.browser_headers
            ).json()
            for g2a_app in game_json_g2a["items"]:
                g2a_app_url = "https://k4g.com/product/" + "-" + g2a_app["slug"] + "-" + str(g2a_app["id"] +
                                                                                             "?r=pricewatch")
                if g2a_app["featured_offer"] is not None:
                    g2a_app_price = str(g2a_app["featured_offer"]["price"]["EUR"]["price"]) + "EUR"
                    g2a_app_name = g2a_app["title"]
                    embed_name = g2a_app_name + " - " + g2a_app_price
                    # Triple checks
                    # 1 check of naam hetzelfde begint
                    # 2 check of elk woord exact overeenkomt (VII =/= VII)
                    # 3 check of game remade of remaster in naam heeft (tinkering?)
                    if g2a_app_name.lower().startswith(game_name.lower()) \
                            and re.search(r'\b' + game_name.lower() + r'\b', g2a_app_name.lower())\
                            and check_base_game(game_name.lower(), g2a_app_name.lower()):
                        prices_embed.add_field(
                            name="K4G - {price}".format(price=g2a_app_price),
                            value="[{name}]({url})".format(name=embed_name, url="{}".format(g2a_app_url))
                        )
            print("out loop")

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
                        choice_data = data[choice-1]
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
    await bot.add_cog(k4g(bot))

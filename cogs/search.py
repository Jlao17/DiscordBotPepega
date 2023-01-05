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
from functions.check_game_exists import check_game_exists
from functions.get_store import g2a,kinguin,k4g
import re


class Search(commands.Cog, name="search"):
    def __init__(self, bot):
        self.bot = bot
        self.wrapper = IGDBWrapper(config["igdbclient"], config["igdbaccess"])
        self.steam_apps = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2").json()
        self.browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
        }

    @commands.hybrid_command(
        name="search",
        description="Search for games",
    )
    async def search(self, ctx, *, args: str):
        """https://api-docs.igdb.com/#about"""
        byte_array = self.wrapper.api_request(
            'games',
            'fields name, alternative_names.*; limit 10; where category = (0,8,9); search "{}";'.format(args)
        )
        data = json.loads(byte_array)
        data = check_game_exists(self.steam_apps, data)

        def get_game(args):
            price_list_g2a, game_data, game_appid = g2a(get_steam_game(self.steam_apps, args))
            price_list_k4g, game_data1, game_appid1 = k4g(get_steam_game(self.steam_apps, args))
            price_list_kinguin, game_data2, game_appid2 = kinguin(get_steam_game(self.steam_apps, args))
            price_list_g2a.sort(key=lambda x: float(x[3]))
            price_list_k4g.sort(key=lambda x: float(x[3]))
            price_list_kinguin.sort(key=lambda x: float(x[3]))
            print(price_list_g2a)
            print(price_list_k4g)
            print(price_list_kinguin)

            prices_embed = discord.Embed(
                title="Price information",
                description=args,
                color=0x9C84EF
            )
            if price_list_g2a:
                prices_embed.add_field(
                    name="G2A - €{price}".format(price=price_list_g2a[0][3]),
                    value="[{name}]({url})".format(name=price_list_g2a[0][1], url=price_list_g2a[0][2])
                )
            if price_list_k4g:
                prices_embed.add_field(
                    name="K4G - €{price}".format(price=price_list_k4g[0][3]),
                    value="[{name}]({url})".format(name=price_list_k4g[0][1], url=price_list_k4g[0][2])
                )
            if price_list_kinguin:
                prices_embed.add_field(
                    name="Kinguin - €{price}".format(price=price_list_kinguin[0][3]),
                    value="[{name}]({url})".format(name=price_list_kinguin[0][1], url=price_list_kinguin[0][2])
                )

            return get_steam_price(game_data, prices_embed, game_appid)

        async def print_game(choice, interaction=None):
            check_name = get_game(choice)
            if check_name is None:
                for alt_name in choice["alternative_names"]:
                    check_name = get_game(alt_name["name"])
            if check_name is None:
                if interaction is None:
                    await ctx.send("Game could not be found on Steam.")
                else:
                    await interaction.followup.send("Game could not be found on Steam.")
            else:
                if interaction is None:
                    await ctx.send(embed=check_name)
                else:
                    await interaction.followup.send(embed=check_name)

        # Search results 0
        if len(data) < 1:
            await ctx.send("I've found no game")
        # Search results more than 1
        elif len(data) > 1:
            game_list = []
            x = 1
            for game in data:
                game_list.append(discord.SelectOption(label=game, value=str(x)))
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
                            # Defer interaction earlier so it does not expire before processing has finished
                            await interaction.response.defer()
                            await print_game(choice_data, interaction)

            select.callback = callback
            view = View()
            view.add_item(select)
            await ctx.send(embed=embed, view=view)
        # Search results one
        else:
            print(len(data), data)
            async with ctx.typing():
                await print_game(data[0])


async def setup(bot):
    await bot.add_cog(Search(bot))

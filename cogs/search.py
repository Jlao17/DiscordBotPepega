import platform

import discord
import requests
import json
from bot import config
from igdb.wrapper import IGDBWrapper
from discord.ext import commands
from discord.ui import *


class Search(commands.Cog, name="search"):
    def __init__(self, bot):
        self.bot = bot
        self.wrapper = IGDBWrapper(config["igdbclient"], config["igdbaccess"])
        self.steam_apps = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2").json()

    @commands.hybrid_command(
        name="search",
        description="Search for games",
    )
    async def search(self, ctx, *, args: str):
        """https://api-docs.igdb.com/#about"""
        byte_array = self.wrapper.api_request(
            'games',
            'fields name; limit 10; where category = 0 & platforms = 6; search "{}";'.format(args)
        )
        data = json.loads(byte_array)
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

            def get_game(args):
                game_appid = None
                print(args)
                for app in self.steam_apps["applist"]["apps"]:
                    if app["name"].lower() == args.lower():
                        print("found it")
                        game_appid = str(app["appid"])
                        break
                if game_appid is None:
                    print("game not found")
                    return

                game_json = requests.get("http://store.steampowered.com/api/appdetails?appids=" + game_appid).json()
                game_data = game_json[game_appid]["data"]
                price = game_data["price_overview"]
                price_currency = price["currency"]
                price_final = price["final"]
                price_discount = price["discount_percent"]

                price_total = game_data["name"] + ": " + price_currency + str(price_final / 100) + \
                              ' ' + str(price_discount) + '% discount'
                return price_total

            async def print_game(interaction, choice):
                check_game = get_game(choice["name"])
                if check_game is None:
                    await interaction.response.send_message("Game could not be found on Steam.")
                else:
                    await interaction.response.send_message(check_game)

            async def callback(interaction):
                if select.values[0] == "1":
                    choice_data = data[0]
                    await print_game(interaction, choice_data)
                if select.values[0] == "2":
                    choice_data = data[1]
                    await print_game(interaction, choice_data)
                if select.values[0] == "3":
                    choice_data = data[2]
                    await print_game(interaction, choice_data)
                if select.values[0] == "4":
                    choice_data = data[3]
                    await print_game(interaction, choice_data)
                if select.values[0] == "5":
                    choice_data = data[4]
                    await print_game(interaction, choice_data)
                if select.values[0] == "6":
                    choice_data = data[5]
                    await print_game(interaction, choice_data)
                if select.values[0] == "7":
                    choice_data = data[6]
                    await print_game(interaction, choice_data)
                if select.values[0] == "8":
                    choice_data = data[7]
                    await print_game(interaction, choice_data)
                if select.values[0] == "9":
                    choice_data = data[8]
                    await print_game(interaction, choice_data)
                if select.values[0] == "10":
                    choice_data = data[9]
                    await print_game(interaction, choice_data)

            select.callback = callback
            view = View()
            view.add_item(select)
            await ctx.send(embed=embed, view=view)
        # Search results one
        else:
            await ctx.send("In progress")

        # Output price for that one game
        # To do:    1. dropdown list if more than one game in list
        #           2. Output prices for selected game


async def setup(bot):
    await bot.add_cog(Search(bot))

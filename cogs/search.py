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

    @commands.hybrid_command(
        name="s",
        description="Search games on steam",
    )
    async def s(self, ctx, *, args: str):
        """
        Search for games on steam using the following link format:
        http://api.steampowered.com/<interface name>/<method name>/v<version>/?key=<api key>&format=<format>

        :param context: The hybrid command context.
        :param args: The game to be searched.
        """

        args = args.lower()
        print(args)
        api_key = config["steam_api"]
        interface = "IStoreService"
        method = "GetAppList"
        version = "v1"

        # responses = requests.get("http://api.steampowered.com/" +
        #                          interface + "/" + method + "/" + version + "/?key=" + api_key)

        steam_apps = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2").json()

        def get_game_id():
            game_id = ""
            for app in steam_apps["applist"]["apps"]:
                if app["name"].lower() == args:
                    game_id = app["appid"]
            return str(game_id)

        game_appid = get_game_id()
        game_json = requests.get("http://store.steampowered.com/api/appdetails?appids=" + game_appid).json()

        game = game_json[game_appid]["data"]
        game_name = game["name"]
        game_description = game["short_description"]
        game_thumbnail = game["header_image"]

        price = game["price_overview"]
        price_currency = price["currency"]
        price_final = price["final"]
        price_discount = price["discount_percent"]

        price_total = price_currency + ' ' + str(price_final/100) + ' ' + str(price_discount) + '% discount'

        print(get_game_id())
        print(json.dumps(game, indent=4))

        embed = discord.Embed(
            title=game_name,
            description=f"{game_description}",
            color=0x9C84EF
        )
        embed.set_thumbnail(url=game_thumbnail)

        await ctx.send(embed=embed)
        await ctx.send(price_total)

    @commands.hybrid_command(
        name="search",
        description="Search for games",
    )
    async def search(self, ctx, *, args: str):
        """https://api-docs.igdb.com/#about"""
        game_list = ""
        byte_array = self.wrapper.api_request(
            'games',
            'fields name; limit 10; where category = 0; search "{}";'.format(args)
        )
        data = json.loads(byte_array)
        print(data, len(data))
        if len(data) < 1:
        #     for game in data:
        #         game_list += game["name"] + "\n"
        #     await ctx.send("I've found {} game{}:\n{}".format(len(data), "" if len(data) < 2 else "s", game_list))
        # else:
            await ctx.send("I've found no game")

        elif len(data) > 1:
            x = 1
            game_list2 = []
            for game in data:
                game_list2.append(discord.SelectOption(label=game["name"], value="{}".format(x)))
                x += 1
            embed = discord.Embed(title="Select game", description="")
            select = Select(
                placeholder="Select a game",
                options=game_list2
            )

            def get_game(args):

                args = args.lower()
                print(args)
                api_key = config["steam_api"]
                interface = "IStoreService"
                method = "GetAppList"
                version = "v1"

                # responses = requests.get("http://api.steampowered.com/" +
                #                          interface + "/" + method + "/" + version + "/?key=" + api_key)

                steam_apps = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2").json()

                def get_game_id():
                    game_id = ""
                    for app in steam_apps["applist"]["apps"]:
                        if app["name"].lower() == args:
                            game_id = app["appid"]
                    return str(game_id)

                game_appid = get_game_id()
                game_json = requests.get("http://store.steampowered.com/api/appdetails?appids=" + game_appid).json()
                game = game_json[game_appid]["data"]
                price = game["price_overview"]
                price_currency = price["currency"]
                price_final = price["final"]
                price_discount = price["discount_percent"]

                price_total = price_currency + "{:,.2f}".format(price_final) + ' ' + price_discount + '% discount'
                return price_total

            async def callback(interaction):
                if select.values[0] == "1":
                    game = data[0]
                    await ctx.send("This costs {}".format(get_game(game["name"])))
                if select.values[0] == "2":
                    game = data[1]
                    await ctx.send("This costs {}".format(get_game(game["name"])))
                if select.values[0] == "3":
                    game = data[2]
                    await ctx.send("This costs {}".format(get_game(game["name"])))
                if select.values[0] == "4":
                    game = data[3]
                    await ctx.send("This costs {}".format(get_game(game["name"])))
                if select.values[0] == "5":
                    game = data[4]
                    await ctx.send("This costs {}".format(get_game(game["name"])))
                if select.values[0] == "6":
                    game = data[5]
                    await ctx.send("This costs {}".format(get_game(game["name"])))
                if select.values[0] == "7":
                    game = data[6]
                    await ctx.send("This costs {}".format(get_game(game["name"])))
                if select.values[0] == "8":
                    game = data[7]
                    await ctx.send("This costs {}".format(get_game(game["name"])))
                if select.values[0] == "9":
                    game = data[8]
                    await ctx.send("This costs {}".format(get_game(game["name"])))
                if select.values[0] == "10":
                    game = data[9]
                    await ctx.send("This costs {}".format(get_game(game["name"])))
            select.callback = callback
            view = View()
            view.add_item(select)
            await ctx.send(embed=embed, view=view)

        else:
            await ctx.send("In progress")
        # Output price for that one game
        # To do:    1. dropdown list if more than one game in list
        #           2. Output prices for selected game


async def setup(bot):
    await bot.add_cog(Search(bot))

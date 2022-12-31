import platform
import traceback
import discord
import requests
import json
from discord.ext import commands
from discord.ext.commands import Context
from bot import config
from helpers.db_connect import startsql as sql
import re


class Steam(commands.Cog, name="steam"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="compare",
        description="compare",
    )
    async def compare(self, ctx, *, args: str):
        stri = "Hermes: War of the Gods - Steam - Key GLOBAL"
        if args in stri:
            await ctx.send("{} is in {}".format(args, stri))
        else:
            await ctx.send("{} is not in {}".format(args, stri))

    @commands.hybrid_command(
        name="fillsteamdb",
        description="compare",
    )
    async def fillsteamdb(self, ctx):
        error = []
        await ctx.send("Filling it up! Will notify any updates")
        steam_apps = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2").json()
        count = 0
        for app in steam_apps["applist"]["apps"]:
            count += 1
            # if normalized_text(app["name"].lower()) == normalized_text(args.lower()):
            game_appid = str(app["appid"])
            game_json_steam = requests.get(
                "http://store.steampowered.com/api/appdetails?appids=" + game_appid + "&l=english&&currency=3"
            ).json()
            print(game_json_steam)
            try:
                game_data = game_json_steam[game_appid]["data"]
                if game_json_steam is not None:
                    if game_data["type"] == "game":
                        game_name = app["name"]
                        game_thumbnail = game_data["header_image"]
                        if game_data["is_free"] == "true":
                            game_price_initial = 0
                            game_price_final = 0
                            game_price_discount = 0
                        else:
                            game_price_initial = game_data["price_overview"]["initial"]
                            game_price_final = game_data["price_overview"]["final"]
                            game_price_discount = game_data["price_overview"]["discount_percent"]
                        game_type = game_data["type"]
                        sql.execute("INSERT INTO "
                                    "steam_games (id, name, steam_id, thumbnail, price_initial, price_final, discount, type) "
                                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                                    (str(count), game_name, str(game_appid), game_thumbnail, str(game_price_initial),
                                     str(game_price_final),
                                     str(game_price_discount), game_type))
            except:
                error.append(game_appid)
                traceback.print_exc()
                if count % 5 == 0:
                    await ctx.send("Failed inserting: {}".format(error))
                    error.clear()

        # await ctx.send("<@186120333726580736> <@160805480644476928> done")


async def setup(bot):
    await bot.add_cog(Steam(bot))

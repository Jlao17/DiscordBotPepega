import platform
import traceback
import discord
import requests
import json
from discord.ext import commands
from discord.ext.commands import Context
from bot import config
from helpers.db_connect import startsql as sql
from ratelimit import limits, sleep_and_retry
import time

class Steam(commands.Cog, name="steam"):
    def __init__(self, bot):
        self.bot = bot
        self.browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
        }

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

    # @commands.hybrid_command(
    #     name="fillsteamdb",
    #     description="compare",
    # )
    # async def fillsteamdb(self, ctx):
    #     error = []
    #     await ctx.send("Filling it up! Will notify any updates")
    #
    #     # rate limit the requests
    #     @sleep_and_retry
    #     @limits(calls=25, period=60)
    #     async def get_json(game_appid):
    #         response = requests.get(
    #             "http://store.steampowered.com/api/appdetails?appids=" + game_appid + "&l=english&&currency=3&format=json",
    #             headers=self.browser_headers
    #         ).json()
    #         return response
    #
    #     async def get_store_apps(store_page, count):
    #         for app in store_page:
    #             count += 1
    #             # if normalized_text(app["name"].lower()) == normalized_text(args.lower()):
    #             game_appid = str(app["appid"])
    #             game_json_steam = await get_json(game_appid)
    #             print("http://store.steampowered.com/api/appdetails?appids=" + game_appid + "&l=english&&currency=3")
    #             try:
    #                 if game_json_steam is None:
    #                     continue
    #                 if "data" not in game_json_steam[game_appid]:
    #                     continue
    #                 else:
    #                     game_data = game_json_steam[game_appid]["data"]
    #                     if game_data["type"] == "game":
    #                         game_name = app["name"]
    #                         game_thumbnail = game_data["header_image"]
    #                         if game_data["is_free"]:
    #                             game_price_initial = 0
    #                             game_price_final = 0
    #                             game_price_discount = 0
    #                         elif game_data["is_free"] is False and "price_overview" not in game_data:
    #                             game_price_initial = "MISSING"
    #                             game_price_final = "MISSING"
    #                             game_price_discount = "MISSING"
    #                         else:
    #                             game_price_initial = game_data["price_overview"]["initial"]
    #                             game_price_final = game_data["price_overview"]["final"]
    #                             game_price_discount = game_data["price_overview"]["discount_percent"]
    #                         game_type = game_data["type"]
    #                         last_modified = app["last_modified"]
    #                         sql.execute("INSERT INTO "
    #                                     "steam_games (id, name, steam_id, thumbnail, price_initial, price_final, "
    #                                     "discount, type, last_modified) "
    #                                     "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
    #                                     (
    #                                         str(count), game_name, str(game_appid), game_thumbnail,
    #                                         str(game_price_initial),
    #                                         str(game_price_final),
    #                                         str(game_price_discount), game_type, last_modified))
    #                         print("added " + game_name + " to database")
    #             except:
    #                 error.append(game_appid)
    #                 traceback.print_exc()
    #                 if count % 5 == 0:
    #                     await ctx.send("Failed inserting: {}".format(error))
    #                     error.clear()
    #                 continue
    #         print("reached end get_store_apps")
    #         return count
    #
    #     # await ctx.send("<@186120333726580736> <@160805480644476928> done")
    #     last_appid = 0
    #     count = 0
    #
    #     print(last_appid)
    #     steam_apps_json = requests.get(
    #         "https://api.steampowered.com/IStoreService/GetAppList/v1/?key=" + config["steam_api"] +
    #         "&last_appid=" + str(last_appid) + "&max_results=50000",
    #         headers=self.browser_headers
    #     ).json()
    #     steam_apps = steam_apps_json["response"]["apps"]
    #     await get_store_apps(steam_apps, count)
    #
    #     await ctx.send("jobs done")

    @commands.hybrid_command(
        name="fillsteamdb",
        description="compare",
    )
    async def fillsteamdb(self, ctx):
        error = []
        await ctx.send("Filling it up! Will notify any updates")

        async def get_store_apps(store_page, count):
            for app in store_page:
                count += 1

                game_appid = str(app["appid"])
                game_name = str(app["name"])
                last_modified = int(app["last_modified"])
                price_change_number = int(app["price_change_number"])

                if game_appid is None or game_name is None or last_modified is None:
                    continue
                else:
                    try:
                        sql.execute("INSERT INTO "
                                    "steamdb (id, name, steam_id, last_modified, price_change_number) "
                                    "VALUES (%s, %s, %s, %s, %s)",
                                    (
                                        str(count), game_name, game_appid, last_modified, price_change_number))
                        print("Added " + game_name + " to database")
                    except:
                        error.append(game_appid)
                        traceback.print_exc()
                        if count % 5 == 0:
                            await ctx.send("Failed inserting: {}".format(error))
                            error.clear()
                        continue
            print("reached end get_store_apps")
            return count

        # await ctx.send("<@186120333726580736> <@160805480644476928> done")
        last_appid = 2142130
        count = 111233

        print(last_appid)
        steam_apps_json = requests.get(
            "https://api.steampowered.com/IStoreService/GetAppList/v1/?key=" + config["steam_api"] +
            "&last_appid=" + str(last_appid) + "&include_dlc=true&max_results=50000",
            headers=self.browser_headers
        ).json()
        steam_apps = steam_apps_json["response"]["apps"]
        await get_store_apps(steam_apps, count)

        await ctx.send("jobs done")


async def setup(bot):
    await bot.add_cog(Steam(bot))

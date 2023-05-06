import traceback
import requests
import asyncio
import json
import time
from discord.ext import commands, tasks
from bot import config
from helpers.db_connectv2 import startsql as sql


class Steam(commands.Cog, name="steam"):
    def __init__(self, bot):
        self.bot = bot
        self.data = {}
        self.data2 = {}
        self.cache = "0"
        self.key = ""
        self.browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
        }
        self.getkey()
        # Comment this if you want to manually disable the steamdb check
        #self.fillsteamdb.start()

    def getkey(self):
        with open('cache.json') as json_file:
            self.data = json.load(json_file)
        self.cache = self.data["cache_steamid"]
        with open('config.json') as json_fil:
            self.data = json.load(json_fil)
        self.key = self.data["steam_api"]

    async def write(self, change):
        with open("cache.json", "w") as json_file:
            self.cache = f"{change}"
            self.data2["cache_steamid"] = self.cache
            json.dump(self.data2, json_file)

    @commands.hybrid_command(
        name="compare",
        description="compare",
    )
    async def compare(self, ctx):
        app = "Counter-Strike"
        if await sql.fetchone("SELECT * FROM steamdb_test WHERE NAME = %s", app) is not None:
            await ctx.send("yes")
        else:
            await ctx.send("no")

    @tasks.loop(hours=24)
    async def fillsteamdb(self):
        print(f"cache is {self.cache}")
        channel = self.bot.get_channel(772579930164035654)
        await channel.send("**LOG** Daily schedule updating DB starting now")
        error = []

        async def get_store_apps(store_page, count):
            start_time = time.time()
            for app in store_page:
                if await sql.fetchone("SELECT * FROM steamdb_test WHERE NAME = %s", app["name"]) is None:
                    await channel.send("**LOG** New game found: `{}`".format(app["name"]))
                    highest_row = await sql.fetchone("SELECT * FROM steamdb_test ORDER BY id DESC LIMIT 1")
                    count = highest_row[0]
                    count += 1
                    game_appid = str(app["appid"])
                    game_name = str(app["name"])
                    last_modified = int(app["last_modified"])
                    price_change_number = int(app["price_change_number"])

                    if game_appid is None or game_name is None or last_modified is None:
                        continue
                    else:
                        try:
                            await sql.execute("INSERT INTO "
                                              "steamdb_test (id, name, steam_id, last_modified, price_change_number) "
                                              "VALUES (%s, %s, %s, %s, %s)",
                                              (
                                                  str(count), game_name, game_appid, last_modified,
                                                  price_change_number))
                            await self.write(game_appid)
                        except:
                            error.append(game_appid)
                            traceback.print_exc()
                            if count % 5 == 0:
                                await channel.send("**LOG** Failed inserting: {}".format(error))
                                error.clear()
                            continue
                else:
                    await self.write(str(app["appid"]))
                    continue
            await channel.send(f"test done `{(time.time() - start_time) / 5000}` "
                               f"For the whole DB this will take "
                               f"`{(time.time() - start_time) / 5000}` x `119462` = "
                               f"`{int((time.time() - start_time) / 5000 * 119461)}`seconds or "
                               f"`{int(((time.time() - start_time) / 5000 * 119461)/60)} minutes`")
            return count

        highest_row = await sql.fetchone("SELECT * FROM steamdb_test ORDER BY id DESC LIMIT 1")
        count = highest_row[0]

        steam_apps_json = requests.get(
            "https://api.steampowered.com/IStoreService/GetAppList/v1/?key=" + self.key +
            "&last_appid=" + str(self.cache) + "&include_dlc=true&max_results=5000",
            headers=self.browser_headers
        ).json()

        while steam_apps_json["response"]["have_more_results"] is True:
            steam_apps = steam_apps_json["response"]["apps"]
            await get_store_apps(steam_apps, count)
            steam_apps_json = requests.get(
                "https://api.steampowered.com/IStoreService/GetAppList/v1/?key=" + self.key +
                "&last_appid=" + str(self.cache) + "&include_dlc=true&max_results=5000",
                headers=self.browser_headers
            ).json()
        await channel.send("jobs done")

    @fillsteamdb.before_loop
    async def before_fillsteamdb(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(1)


async def setup(bot):
    await bot.add_cog(Steam(bot))

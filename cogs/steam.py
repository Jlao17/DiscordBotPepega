import traceback
import requests
import asyncio
import json
import time
from discord.ext import commands, tasks
from bot import config
from helpers.db_connectv2 import startsql as sql
import datetime
import logging

log = logging.getLogger(__name__)

utc = datetime.timezone.utc
eneba_csv_time = datetime.time(hour=0, minute=0, tzinfo=utc)


class Steam(commands.Cog, name="steam"):
    def __init__(self, bot):
        self.bot = bot
        self.data = {}
        self.data_cache = {"cache_steamid": "0", "cache_steamid_test": "0"}
        self.cache = "0"
        self.key = ""
        self.browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
        }
        self.getkey()
        # Comment this if you want to manually disable the steamdb check
        self.fillsteamdb.start()
        self.get_eneba_csv.start()

    def getkey(self):
        with open('cache.json') as json_file:
            self.data_cache = json.load(json_file)
        self.cache = self.data_cache["cache_steamid"]
        with open('config.json') as json_fil:
            self.data = json.load(json_fil)
        self.key = self.data["steam_api"]

    async def write(self, change):
        self.cache = f"{change}"
        self.data_cache["cache_steamid"] = self.cache
        with open("cache.json", "w") as json_file:
            json.dump(self.data_cache, json_file)

    @commands.hybrid_command(
        name="compare",
        description="compare",
    )
    async def compare(self, ctx):
        app = "Counter-Strike"
        if await sql.fetchone("SELECT * FROM steamdb WHERE NAME = %s", app) is not None:
            await ctx.send("yes")
        else:
            await ctx.send("no")

    @tasks.loop(hours=24)
    async def fillsteamdb(self):
        log.info(f"cache is {self.cache}")
        channel = self.bot.get_channel(772579930164035654)
        await channel.send("**LOG** Daily schedule updating DB starting now")
        error = []

        async def get_store_apps(store_page, count):
            error_count = 0
            start_time = time.time()
            for app in store_page:
                database_row = await sql.fetchone("SELECT * FROM steamdb WHERE steam_id = %s", app["appid"])
                if database_row is None:
                    # await channel.send("**LOG** New game found: `{}`".format(app["name"]))
                    log.info("**LOG** New game found: `{}`".format(app["name"]))
                    highest_row = await sql.fetchone("SELECT * FROM steamdb ORDER BY id DESC LIMIT 1")
                    count = highest_row[0] if highest_row is not None else 0
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
                                              "steamdb (id, name, steam_id, last_modified, price_change_number) "
                                              "VALUES (%s, %s, %s, %s, %s)",
                                              (
                                                  count, game_name, game_appid, last_modified,
                                                  price_change_number))
                            await self.write(game_appid)
                        except:
                            error_count += 1
                            error.append(game_appid)
                            traceback.print_exc()
                            if count % 5 == 0:
                                await channel.send("**LOG** Failed inserting: {}".format(error))
                                error.clear()
                            continue

                # Check if it's the same -> ignore, if not -> update row
                else:
                    if database_row[1] == app["name"]:
                        await self.write(app["appid"])
                        continue
                    else:
                        log.info("**LOG** Updating row in steamdb: `{}` to `{}`".format(database_row[1],app["name"]))
                        count = database_row[0]
                        game_appid = str(app["appid"])
                        game_name = str(app["name"])
                        last_modified = int(app["last_modified"])
                        price_change_number = int(app["price_change_number"])

                        if game_appid is None or game_name is None or last_modified is None:
                            continue
                        else:
                            try:
                                print(game_appid, game_name, last_modified, price_change_number, count)
                                await sql.execute("UPDATE steamdb SET id = %s, name = %s, last_modified = %s, price_change_number = %s WHERE steam_id = %s",
                                                  (str(count), game_name, last_modified, price_change_number, str(game_appid)))
                                await self.write(game_appid)
                            except:
                                error_count += 1
                                error.append(game_appid)
                                traceback.print_exc()
                                if error_count % 5 == 0:
                                    await channel.send("**LOG** Failed updating: {}".format(error))
                                    error.clear()
                                continue

                # else:
                #     await self.write(str(app["appid"]))
                #     continue
            await channel.send(f"test done `{(time.time() - start_time) / 5000}` "
                               f"For the whole DB, this will take "
                               f"`{(time.time() - start_time) / 5000}` x `135115` = "
                               f"`{int(((time.time() - start_time) / 5000 * 135115)/60)}` minutes or"
                               f"`{int(((time.time() - start_time) / 5000 * 135115)/60/60)}` hours")
            # Last page 25/10/2023 appid = 2655390 page 28, 115 items (27 pages x 5000 + 115 = 135115)
            return count

        highest_row = await sql.fetchone("SELECT * FROM steamdb ORDER BY id DESC LIMIT 1")
        count = highest_row[0]
        steam_apps_json = requests.get(
            "https://api.steampowered.com/IStoreService/GetAppList/v1/?key=" + self.key +
            "&last_appid=" + str(self.cache) + "&include_dlc=true&max_results=5000",
            headers=self.browser_headers
        ).json()
        try:
            while steam_apps_json["response"]["have_more_results"] is True:
                steam_apps = steam_apps_json["response"]["apps"]
                await get_store_apps(steam_apps, count)
                steam_apps_json = requests.get(
                    "https://api.steampowered.com/IStoreService/GetAppList/v1/?key=" + self.key +
                    "&last_appid=" + str(self.cache) + "&include_dlc=true&max_results=5000",
                    headers=self.browser_headers
                ).json()
        except KeyError:
            steam_apps = steam_apps_json["response"]["apps"]
            await get_store_apps(steam_apps, count)

        await channel.send("jobs done")
        await self.write("0")

    @fillsteamdb.before_loop
    async def before_fillsteamdb(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(1)

    @tasks.loop(time=eneba_csv_time)
    async def get_eneba_csv(self):
        log.info("start feed parsing")
        url = "https://www.eneba.com/rss/products.csv?version=3&af_id=PriceWatch"
        with requests.Session() as s:
            download = s.get(url)
            url_content = download.content
            csv_clear = open('eneba_csv.csv', 'w')
            csv_clear.close()
            csv_file = open('eneba_csv.csv', 'ab')
            csv_file.write(url_content)
            csv_file.close()

    @get_eneba_csv.before_loop
    async def before_get_eneba_csv(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(1)

    async def gen_igdb_token(self):
        url = 'https://id.twitch.tv/oauth2/token'
        myobj = {'client_id': 'pdc47af0fviuz6lbxylft3jfdmb7kf',
                 'client_secret': 'zuit09gobsu3f290avfz1mqu70xna1',
                 'grant_type': 'client_credentials'
                 }

        x = requests.post(url, json=myobj)
        print(x.text)


async def setup(bot):
    await bot.add_cog(Steam(bot))

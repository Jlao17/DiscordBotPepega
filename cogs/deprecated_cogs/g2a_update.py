from discord.ext.commands import Context
import requests
import asyncio
import json
import time
import discord
from discord.ext import commands, tasks
from helpers.db_connectv2 import startsql as sql
import logging
from igdb.wrapper import IGDBWrapper
import re
import aiohttp
from bot import config

log = logging.getLogger(__name__)

g2a_allowed_platforms = ["Steam", "Origin", "Ubisoft Connect", "GOG.COM", "Epic games", "Microsoft", "Battle.net",
                         "Brawlhalla", "Rockstar", "NCSoft", "Official Website", "Final Fantasy", "Microsoft Store",
                         "Other", "Call of Duty official", "Paladins", "Epic", "TESO", "The Elder Scrolls Online",
                         "Giants", "In Game", "Minecraft", "thesims3.com", "SMITE", "Star Trek Online", "Black Desert",
                         "Battlestate", "Arena.net", "Bungie", "Blizzard", "Warframe", "Telltale Games",
                         "Rockstar Social Club", "Square Enix", "Bloodhunt", "Stronghold Kingdoms", "Introversion",
                         "Trion Worlds", "Techlandgg"]
g2a_filter_keywords = ["key", "steam", "global", "pc", "europe", "ru/cis", "gift", "origin", "ubisoft", "gog.com",
                       "north america", "latam", "dlc", "battle.net", "|"]

g2a_allowed_regions = ["GLOBAL", "EUROPE", "NORTH AMERICA", "EUROPE / NORTH AMERICA"]


def remove_keywords(offer_name):
    # Split the offer name into words
    words = offer_name.split()
    # Remove the keywords from the offer name if they occur only once. If they occur twice, only remove the second one.
    for keyword in g2a_filter_keywords:
        if keyword in words:
            index = words.index(keyword)
            words = words[:index]

    # Join the words back together
    filtered_offer_name = " ".join(words)
    return filtered_offer_name


async def get_tasks(session, games):
    tasks = []
    igdb_url = "https://api.igdb.com/v4/games"
    payload = "fields name, external_games.uid, external_games.category; limit 10; where " \
              "external_games.category = 1; search \"{}\"; "
    headers = {
        'Authorization': 'Bearer ' + config["igdbaccess"],
        'Client-ID': config["igdbclient"],
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0"
    }
    for game in games:
        tasks.append(asyncio.create_task(session.post(url=igdb_url,
                                                      data=payload.format(game[0]),
                                                      headers=headers, ssl=False)))
    return tasks


async def post_request(games):
    results = []
    names_list = []
    responses_list = []
    async with aiohttp.ClientSession() as session:
        for game in games:
            await asyncio.sleep(0.25)
            names_list.append(game)
            if len(names_list) % 2 == 0:
                retrieve_tasks = await get_tasks(session, names_list)
                responses = await asyncio.gather(*retrieve_tasks)
                for response in responses:
                    responses_list.append(response)
                names_list = []
        for index, (response, game) in enumerate(zip(responses_list, games)):
            result = await response.json()
            if len(result) < 1:
                log.info("No results found for {}".format(game[0]))
                continue
            # Get the first steam_id from the result
            steam_id = None
            try:
                igdb_names = result[0]["external_games"]
            except Exception as e:
                log.info(e)
                continue
            for names in igdb_names:
                if names["category"] == 1:
                    steam_id = names["uid"]
                    break

            # Add the steam_id to the corresponding game
            if steam_id is not None:
                games[index] += (steam_id,)

            results.append(games[index])
    return results


class G2aUpdate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.g2a_cache = {"cache_g2a_page": 1, "cache_g2a_id": 1, "cache_unique_keywords": []}
        self.g2a_page_cache = 1
        self.g2a_id_cache = 1
        self.unique_keywords = []
        self.get_g2a_cache()
        self.fill_g2a_db.start()

    def get_g2a_cache(self):
        with open("cache_g2a.json") as g2a_json:
            self.g2a_cache = json.load(g2a_json)
        self.g2a_page_cache = self.g2a_cache["cache_g2a_page"]
        self.g2a_id_cache = self.g2a_cache["cache_g2a_id"]
        self.unique_keywords = self.g2a_cache["cache_unique_keywords"]

    def write_g2a_cache(self, page, id, keywords):
        self.g2a_page_cache = page
        self.g2a_id_cache = id
        self.unique_keywords = keywords
        self.g2a_cache = {"cache_g2a_page": self.g2a_page_cache, "cache_g2a_id": self.g2a_id_cache,
                          "cache_unique_keywords": self.unique_keywords}
        with open("cache_g2a.json", "w") as g2a_json:
            json.dump(self.g2a_cache, g2a_json)

    @tasks.loop(hours=24)
    async def fill_g2a_db(self):
        log.info("start adding g2a data")
        total_pages = 1781
        while self.g2a_page_cache <= total_pages:
            start = time.time()
            game_info = []
            # G2A API call
            url = "https://api.g2a.com/v1/products"
            params = {
                "page": self.g2a_page_cache
            }

            headers = {
                "Authorization": config["g2a_client_id"] + ", " + config["g2a_api"],
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",

            }

            request = requests.get(url, params=params, headers=headers).json()
            total_pages = request["total"] / 20
            # Iterate over the items in the response
            for item in request["docs"]:
                if item["platform"] not in g2a_allowed_platforms:
                    continue

                offer_name = item["name"]
                offer_url = "https://g2a.com{}?gtag=9b358ba6b1".format(item["slug"])
                offer_price = item["retail_min_price"]
                offer_last_modified = time.time()
                offer_g2a_id = item["id"]
                offer_region = item["region"]

                # Check if offer region is EU, NA or GLOBAL
                if offer_region not in g2a_allowed_regions:
                    continue

                if offer_region == "EUROPE / NORTH AMERICA":
                    offer_region = "GLOBAL"

                # Check if offer name does not contain non ascii characters
                remove_non_ascii = re.sub(r'[^\x00-\x7F]+', '', offer_name.lower())

                # Check if offer name contains any of the characters and remove if present
                standardized_offer_name = remove_non_ascii.lower().replace('(', '').replace(')', '').replace('+', '') \
                    .replace('|', '').replace('"', '').replace('-', '')

                # Check if offer name contains any of the keywords and remove if present
                filtered_offer_name = remove_keywords(standardized_offer_name)

                # Add game info to list for further use
                game_info.append(
                    (filtered_offer_name, offer_name, offer_url, offer_price, offer_last_modified, offer_g2a_id,
                     offer_region))

            results = await post_request(game_info)

            # Iterate over the games_info_steamid list and update the games in the database
            for game in results:
                # Check if a row is present in the database
                db_offer_name = game[1]
                db_offer_url = game[2]
                db_offer_price = game[3]
                db_offer_last_modified = game[4]
                db_offer_g2a_id = game[5]
                db_offer_region = game[6]
                db_steam_id = game[7]

                row_present = await sql.fetchone("SELECT COUNT(1) FROM g2a WHERE id = %s AND g2a_id = %s",
                                                 (db_steam_id, db_offer_g2a_id))

                if row_present[0] == 1:
                    # Update existing row
                    await sql.execute("UPDATE g2a SET key_name = %s, url = %s, price = %s, last_modified = %s "
                                      "WHERE id = %s AND g2a_id = %s",
                                      (db_offer_name, db_offer_url, db_offer_price, db_offer_last_modified, db_steam_id,
                                       db_offer_g2a_id))
                    log.info("updated {} in database".format(db_offer_name))
                else:
                    # Insert new row
                    g2a_convert_region = {"GLOBAL" : "global", "EUROPE": "eu", "NORTH AMERICA": "na", "EUROPE / NORTH AMERICA": "global"}
                    await sql.execute(
                        "INSERT INTO g2a (id, key_name, url, price, last_modified, g2a_id, region) VALUES "
                        "(%s, %s, %s, %s, %s, %s, %s)",
                        (db_steam_id, db_offer_name, db_offer_url,
                         db_offer_price, db_offer_last_modified, db_offer_g2a_id, g2a_convert_region[db_offer_region]))
                    log.info("added {} in database".format(db_offer_name))

            try:
                self.write_g2a_cache(self.g2a_page_cache + 1, offer_g2a_id, self.unique_keywords)
            except Exception as e:
                log.info(e)
                self.write_g2a_cache(self.g2a_page_cache + 1, 1, self.unique_keywords)

            end = time.time()
            log.info("page took: {} seconds".format(end - start))
        log.info("finished adding g2a data")
        # Reset cache
        self.write_g2a_cache(1, 1, [])

    @fill_g2a_db.before_loop
    async def before_fill_g2a_db(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(1)


async def setup(bot):
    await bot.add_cog(G2aUpdate(bot))
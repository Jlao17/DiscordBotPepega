import discord
import requests
import json
from bot import config
from igdb.wrapper import IGDBWrapper
from discord.ext import commands
from discord.ui import View, Select
from functions.get_steam_price import get_steam_price, get_steam_price_dollar
from functions.get_steam_game import get_steam_game
from functions.check_game_in_db import check_game_in_db
from functions.get_stores_functions.get_g2a import get_g2a as g2a
from functions.get_stores_functions.get_kinguin import get_kinguin as kinguin
from functions.get_stores_functions.get_k4g import get_k4g as k4g
from functions.get_stores_functions.get_driffle import get_driffle as driffle
from functions.get_stores_functions.get_eneba import get_eneba as eneba
from functions.get_stores_functions.get_fanatical import get_fanatical as fanatical
from functions.update_steamdb_game import update_steamdb_game
from functions.check_steamlink import check_steamlink
from components.views.SupportView import SupportView
from components.views.StoreView import StoreView
from helpers.db_connectv2 import startsql as sql
from functions.currency_converter import todollar, toeur
import asyncio

import time
import logging

log = logging.getLogger(__name__)
# Constants for get_game function
DB_ID = 0
GAME_NAME = 1
APP_ID = 2
GAME_HEADER = 3
PRICE = 5
LAST_UPDATED = 10

# Constants for game select callback
CHOICE = 0


class Pricewatch(commands.Cog, name="pricewatch"):
    def __init__(self, bot):
        self.bot = bot
        self.wrapper = IGDBWrapper(config["igdbclient"], config["igdbaccess"])
        self.steam_apps = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2").json()
        self.browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
        }
        self.stores = {
                       # g2a: "G2A",
                       k4g: "K4G",
                       kinguin: "Kinguin",
                       # fanatical: "Fanatical",
                       driffle: "Driffle",
                       # eneba: "Eneba"
        }

    @commands.hybrid_command(
        name="search",
        description="Search for games",
    )
    async def search(self, ctx, *, args: str) -> None:
        """https://api-docs.igdb.com/#about"""
        data = []
        # Check if string is a link (steam) 0 = precheck
        linkcheck = check_steamlink(args, 0)
        if linkcheck[0]:
            args = int(linkcheck[1])
            data.append(args)
        else:
            # Else use IGDB
            try:
                byte_array = self.wrapper.api_request(
                    'games',
                    'fields name, alternative_names.*, external_games.uid, external_games.category; limit 10; where external_games.category = 1; search "{}";'.format(
                        args)
                )
            except TypeError:
                await ctx.send("API outputted None")
                return
            data = json.loads(byte_array)
            log.info(data)

        async def get_game(game_args):
            result = await check_game_in_db(game_args)
            if isinstance(game_args, int):
                game_args = {"name": result[GAME_NAME]}
            check = 0
            # If the game cannot be found in db, exit the search command
            if result is None:
                get_game.error_message = "We were unable to find the game on our end. Please contact " \
                                         "us if the game exists on Steam. As for DLCs, we kindly request a Steam URL."
                return None, None, None

            # Check for 1st update db
            elif result[LAST_UPDATED] is None or int(time.time()) - int(result[LAST_UPDATED]) > 43200:
                log.info("First update or longer than 12 hours - SteamDB")
                game_data, app_name = get_steam_game(result[APP_ID])
                if game_data is None:
                    get_game.error_message = "The game is no longer extant on the Steam platform. If this is an " \
                                             "error, kindly notify us via our support server."
                    return None, None, None
                await update_steamdb_game(game_data, result[APP_ID])
            else:
                log.info("Less than 12 hours - SteamDB")
                # Use the current data in db
                check = 1
                if result[PRICE] == "Free":
                    game_data = ["Free", result[GAME_HEADER]]
                else:
                    game_data = [f"€{(int(result[PRICE]) / 100):.2f}", result[GAME_HEADER]]

            # Retrieve user config
            user_cnf = await sql.fetchone("SELECT * FROM user_cnf WHERE userid = {0}".format(ctx.author.id))

            # You see 2 result[1]. It used to be game_name and app_name
            # to combat steam appdetails game name difference, might fix later
            price_lists = []

            # asyncio.gather does the multithreading part
            # for store in self.stores:
            stores_data = await asyncio.gather(*[i(result[GAME_NAME], result[GAME_NAME], result[DB_ID], game_args, self.stores.get(i), user_cnf) for i in self.stores])
            for retrieve in stores_data:
                # retrieve = await store(result[GAME_NAME], result[GAME_NAME], result[DB_ID], game_args, self.stores.get(store), user_cnf)
                retrieve.sort(key=lambda x: 0 if x[3] == '' else float(x[3]))
                price_lists.append(retrieve)

            prices_embed = discord.Embed(
                title="Price information",
                description=result[GAME_NAME],
                color=0x9C84EF
            )

            count = 0

            for store in self.stores:
                if any(price_lists[count]):
                    if user_cnf[2] == "dollar":
                        price = await todollar(price_lists[count][0][3])
                    else:
                        price = await toeur(price_lists[count][0][3])
                    prices_embed.add_field(
                        name="{} - {}".format(self.stores.get(store), price),
                        value="[{name}]({url})".format(name=price_lists[count][0][1], url=price_lists[count][0][2])
                    )
                count += 1

            if check == 0:
                if user_cnf[2] == "dollar":
                    return get_steam_price_dollar(game_data, prices_embed, result[APP_ID]), price_lists, user_cnf
                else:
                    return get_steam_price(game_data, prices_embed, result[APP_ID]), price_lists, user_cnf
            else:
                if user_cnf[2] == "dollar":
                    return get_steam_price_dollar(game_data, prices_embed, result[APP_ID], check=1), price_lists, user_cnf
                else:
                    return get_steam_price(game_data, prices_embed, result[APP_ID], check=1), price_lists, user_cnf

        async def print_game(choice, interaction=None):
            loading_embed = discord.Embed(
                title="Retrieving information...",
                color=0x9C84EF
            )
            loading_embed.set_image(
                url="https://cdn.discordapp.com/attachments/421360319965822986/1105581766208655541/9a81c800a29d2516c25cbfa63b21710f.gif")
            load_msg = await ctx.send(embed=loading_embed)
            check_name, price_lists, user_cnf = await get_game(choice)

            store_data = []
            x = 0
            if price_lists:
                for store in self.stores:
                    store_data.append((price_lists[x], self.stores.get(store)))
                    x += 1

            await load_msg.delete()
            if check_name is None:
                await ctx.send(get_game.error_message)
            else:
                if interaction is None:
                    # Check if all lists are empty so no view is needed
                    if not any(price_lists):
                        await ctx.send(embed=check_name)
                    else:
                        await ctx.send(embed=check_name, view=StoreView(store_data, user_cnf))
                else:
                    if not any(price_lists):
                        await interaction.followup.send(embed=check_name)
                    else:
                        await interaction.followup.send(embed=check_name, view=StoreView(store_data, user_cnf))

        # Search results more than 1
        if len(data) > 1:
            game_list = []
            check = []
            x = 1
            for game in data:
                # Removes 'duplicates' from IGDB
                if game["name"] not in check:
                    check.append(game["name"])
                    game_list.append(discord.SelectOption(label=game["name"], value=str(x)))
                    x += 1
            embed = discord.Embed(title="Select game", description="")
            select = Select(
                placeholder="Select a game",
                options=game_list
            )

            async def callback(interaction):
                for choice in range(0, 11):
                    if select.values[CHOICE] == str(choice):
                        # Defer interaction earlier, so it does not expire before processing has finished
                        await interaction.response.defer()
                        await print_game(data[choice - 1], interaction)
            select.callback = callback
            view = View()
            view.add_item(select)
            await ctx.send(embed=embed, view=view)
        # Search results one
        elif len(data) == 1:
            async with ctx.typing():

                await print_game(data[0])
        else:
            await ctx.send(f"We were unable to locate a game or DLC titled `{args}`. If this is an error, kindly "
                           f"provide us with a Steam link or inform us of the issue.",
                           view=SupportView(args, self.bot))

    @commands.hybrid_command(
        name="region",
        description="Change your region: NA, EU or GLOBAL",
    )
    async def region(self, ctx, *, region: str) -> None:
        print(ctx.author.id)
        if await sql.fetchone("SELECT * FROM user_cnf WHERE userid = %s", ctx.author.id) is None:
            log.info("no")
            await sql.execute("INSERT INTO user_cnf (userid) VALUES (%s)", ctx.author.id)
        if region.lower() not in ["eu", "na", "global"]:
            await ctx.send("[**Error**] Please select one of the following regions: `eu`, `na` or `global`")
            return

        await sql.execute("UPDATE user_cnf SET region = %s WHERE userid = %s", (region.lower(), ctx.author.id))
        await ctx.send(f"You've chosen {region} as the preferred region")

    @commands.hybrid_command(
        name="currency",
        description="Change your currency: euro, dollar or pound",
    )
    async def currency(self, ctx, *, currency: str) -> None:
        if await sql.fetchone("SELECT * FROM user_cnf WHERE userid = %s", ctx.author.id) is None:
            await sql.execute("INSERT INTO user_cnf (userid) VALUES (%s)", ctx.author.id)
        if currency.lower() not in ["euro", "dollar"]: #"pound"]:
            await ctx.send("[**Error**] Please select one of the following regions: `euro`, `dollar` or `pound`")
            return
        await sql.execute("UPDATE user_cnf SET currency = %s WHERE userid = %s", (currency.lower(), ctx.author.id))
        await ctx.send(f"You've chosen {currency} as the preferred currency")


async def setup(bot):
    await bot.add_cog(Pricewatch(bot))

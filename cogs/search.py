import discord
import requests
import json
from bot import config
from igdb.wrapper import IGDBWrapper
from discord.ext import commands, tasks
from discord.ui import View, Select
from discord import app_commands
from typing import Literal
from functions.get_steam_price import get_steam_price
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
from functions.currency_converter import todollar, toeur, topound
import asyncio
import re
import datetime
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

utc = datetime.timezone.utc
check_alerts_time = datetime.time(hour=1, minute=0, tzinfo=utc)


class Pricewatch(commands.Cog, name="pricewatch"):
    def __init__(self, bot):
        self.bot = bot
        self.wrapper = IGDBWrapper(config["igdbclient"], config["igdbaccess"])
        self.steam_apps = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2").json()
        self.browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
        }
        self.stores = {
            g2a: "G2A",
            k4g: "K4G",
            kinguin: "Kinguin",
            fanatical: "Fanatical",
            # driffle: "Driffle",
            eneba: "Eneba"
        }

    @commands.hybrid_command(
        name="search",
        description="Search for games",
    )
    async def search(self, ctx, *, game: str) -> None:
        """https://api-docs.igdb.com/#about"""
        """Search a game for prices

        Args:
            game: game to add using name or Steam URL
        """
        data = []
        # Check if string is a link (steam) 0 = precheck
        linkcheck = await check_steamlink(game, 0)
        if linkcheck[0]:
            game = int(linkcheck[1])
            data.append(game)
        else:
            # Else use IGDB
            try:
                byte_array = self.wrapper.api_request(
                    'games',
                    'fields name, alternative_names.*, external_games.uid, external_games.category; limit 10; where external_games.category = 1; search "{}";'.format(
                        game)
                )
            except TypeError:
                await ctx.send("API outputted None")
                return
            data = json.loads(byte_array)
            log.info(data)

        async def get_game(game_args):
            result = await check_game_in_db(game_args)

            if isinstance(game_args, int):
                try:
                    game_args = {"name": result[GAME_NAME]}
                except TypeError:
                    result = None

            check = 0
            # If the game cannot be found in db, exit the search command
            if result is None:
                get_game.error_message = "We were unable to find the game on our end. Please contact " \
                                         "us if the game exists on Steam. As for DLCs, we kindly request a Steam URL."
                return None, None, None

            # Retrieve user config
            user_cnf = await sql.fetchone("SELECT * FROM user_cnf WHERE userid = %s", ctx.author.id)
            if not user_cnf:
                await sql.execute("INSERT INTO user_cnf (userid) VALUES (%s)", ctx.author.id)
                user_cnf = await sql.fetchone("SELECT * FROM user_cnf WHERE userid = %s", ctx.author.id)
            # user_cnf = await sql.fetchone("SELECT * FROM user_cnf WHERE userid = {0}".format(ctx.author.id))

            # Check for 1st update db
            elif result[LAST_UPDATED] is None or int(time.time()) - int(result[LAST_UPDATED]) > 43200:
                log.info("First update or longer than 12 hours - SteamDB")
                game_data, app_name = get_steam_game(result[APP_ID], user_cnf)
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

            # You see 2 result[1]. It used to be game_name and app_name
            # to combat steam appdetails game name difference, might fix later
            price_lists = []

            # asyncio.gather does the multithreading part
            # for store in self.stores:
            stores_data = await asyncio.gather(
                *[i(result[GAME_NAME], result[DB_ID], game_args, self.stores.get(i), user_cnf) for i in self.stores])
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

            # Fanatical uses Steam prices
            for store in self.stores:
                # Check if price list is empty or not
                log.info(price_lists[count])
                if len(price_lists[count]) != 0:
                    if self.stores.get(store) == "Fanatical":
                        if user_cnf[2] == "euro":
                            price = "€{}".format(price_lists[count][0][3])
                        if user_cnf[2] == "dollar":
                            price = "${}".format(price_lists[count][0][4])
                        if user_cnf[2] == "pound":
                            price = "£{}".format(price_lists[count][0][5])
                    else:
                        if any(price_lists[count]):
                            if user_cnf[2] == "dollar":
                                price = await todollar(price_lists[count][0][3])
                            elif user_cnf[2] == "euro":
                                price = await toeur(price_lists[count][0][3])
                            elif user_cnf[2] == "pound":
                                price = await topound(price_lists[count][0][3])
                    print(price_lists[count])
                    prices_embed.add_field(
                        name="{} - {}".format(self.stores.get(store), price),
                        value="[{name}]({url})".format(name=price_lists[count][0][1], url=price_lists[count][0][2])
                    )
                else:
                    log.info(f"Skipping store {self.stores.get(store)}, price list empty")
                count += 1

            if check == 0:
                return get_steam_price(game_data, prices_embed, result[APP_ID], user_cnf), price_lists, user_cnf
            else:
                return get_steam_price(game_data, prices_embed, result[APP_ID], user_cnf,
                                       check=1), price_lists, user_cnf

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
                    if interaction.user.id == ctx.author.id:
                        if select.values[CHOICE] == str(choice):
                            # Defer interaction earlier, so it does not expire before processing has finished
                            await interaction.response.defer()
                            await print_game(data[choice - 1], interaction)
                    else:
                        await interaction.followup.send("You are not allowed to use this command!", ephemeral=True)

            select.callback = callback
            view = View()
            view.add_item(select)
            await ctx.send(embed=embed, view=view)
        # Search results one
        elif len(data) == 1:
            async with ctx.typing():

                await print_game(data[0])
        else:
            await ctx.send(f"We were unable to locate a game or DLC titled `{game}`. If this is an error, kindly "
                           f"provide us with a Steam link or inform us of the issue.",
                           view=SupportView(game, self.bot))

    @commands.hybrid_command(
        name="region",
        description="Change your region: NA, EU or GLOBAL",
    )
    async def region(self, ctx, *, region: Literal["NA", "EU", "Global"]) -> None:
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
        description="Change your currency: euro or dollar",
    )
    async def currency(self, ctx, *, currency: Literal["Euro", "Dollar", "Pound"]) -> None:
        if await sql.fetchone("SELECT * FROM user_cnf WHERE userid = %s", ctx.author.id) is None:
            await sql.execute("INSERT INTO user_cnf (userid) VALUES (%s)", ctx.author.id)
        if currency.lower() not in ["euro", "dollar", "pound"]:
            await ctx.send("[**Error**] Please select one of the following regions: `euro`, `dollar` or `pound`")
            return
        await sql.execute("UPDATE user_cnf SET currency = %s WHERE userid = %s", (currency.lower(), ctx.author.id))
        await ctx.send(f"You've chosen {currency} as the preferred currency")

    # @commands.hybrid_command(
    #     name="alert",
    #     description="Show, add or remove your alerts",
    # )
    # async def alert(self, ctx, *, type: Literal["show", "add", "remove"], args):
    #     # Show user's alerts
    #     if type.lower() == "show":
    #         alerts = await sql.fetchall("SELECT * FROM alerts WHERE userid = %s", ctx.author.id)
    #         log.info(alerts)
    #         if alerts is None:
    #             await ctx.send("No alerts..")
    #         else:
    #             alerts_embed = discord.Embed(
    #                 title=f"{ctx.author.name}'s Alerts",
    #                 description=f"{len(alerts)}/10 used alerts",
    #                 color=0x800080
    #             )
    #             count = 1
    #             for alert in alerts:
    #                 log.info(alert)
    #                 alerts_embed.add_field(name=f"{count}. {alert[1]} - <€{alert[2]}", value="", inline=False)
    #                 count += 1
    #             await ctx.send(embed=alerts_embed)
    #
    #     # Add user's alerts
    #     elif type.lower() == "add":
    #         log.info(args)
    #         if args.lower() == "help":
    #             await ctx.send("To add a list, do /alert add `<steam_game_url>` or `<steam_game_id>`\n"
    #                            "`/alert add https://store.steampowered.com/app/413150/Stardew_Valley/`")
    #         else:
    #             await ctx.send("Adding alerts...")
    #
    #     # Remove user's alerts
    #     elif type.lower() == "remove":
    #         await ctx.send("Removing alerts...")

    @staticmethod
    async def is_valid_currency_number(currency):
        # Replace commas with dots
        currency = currency.replace(',', '.')

        # Define the regular expression pattern for a valid currency number
        pattern = re.compile(r'^\d+(?:[.,]\d{1,2})?$')

        # Check if the input matches the pattern
        if pattern.match(currency) and len(currency) < 6:
            return True
        else:
            return False

    @commands.hybrid_group(
        description="Show, add or remove your alerts",
    )
    async def alert(self, ctx):
        await ctx.send("alert show, alert add `<steam_game_url>`/`<steam_game_id>` `<price>`, alert remove "
                       "`<id>` (shown in alert show)")

    @alert.command(
        description="Shows your current alerts",
    )
    async def show(self, ctx):
        alerts = await sql.fetchall("SELECT * FROM alerts WHERE userid = %s", ctx.author.id)
        log.info(alerts)
        if alerts is None:
            await ctx.send("No alerts..")
        else:
            userdata = await sql.fetchone("SELECT * FROM user_cnf WHERE userid = %s", ctx.author.id)
            if userdata[3] == 0:
                max = 10
            elif userdata[3] == 1:
                max = 20
            currency = {"euro": "€", "dollar": "$", "pound": "£"}

            alerts_embed = discord.Embed(
                title=f"{ctx.author.name}'s Alerts",
                description=f"{len(alerts)}/{max} used alerts",
                color=0x800080
            )
            count = 1
            for alert in alerts:
                log.info(alert)
                alerts_embed.add_field(name=f"{count}. {alert[1]} - <{currency[userdata[2]]}{alert[2]}", value="",
                                       inline=False)
                count += 1
            await ctx.send(embed=alerts_embed)

    @alert.command(
        description="Add alerts: alert add <steam_game_url>/<steam_game_id> <price>",
    )
    async def add(self, ctx, game, price):
        """Add a game for alert

        Args:
            game: game to add using name or Steam URL
            price: alerts you when this price is met
        """

        data = []
        # Check if string is a link (steam) 0 = precheck
        linkcheck = await check_steamlink(game, 0)
        pricecheck = await self.is_valid_currency_number(price)
        if linkcheck[0] and pricecheck:
            args = int(linkcheck[1])
            game = await sql.fetchone("SELECT * FROM steamdb WHERE steam_id = %s", args)
            if game:
                userdata = await sql.fetchone("SELECT * FROM user_cnf WHERE userid = %s", ctx.author.id)
                if userdata[3] == 0:
                    max = 10
                elif userdata[3] == 1:
                    max = 20

                if len(await sql.fetchall("SELECT * FROM alerts WHERE userid = %s", ctx.author.id)) > (max - 1):
                    await ctx.send("*Error*: Max alerts reached")
                else:
                    price = price.replace(',', '.')
                    if '.' not in price:
                        price += '.00'
                    await sql.execute("INSERT INTO alerts (userid, game, price, premium) VALUES (%s, %s, %s, %s)",
                                      (ctx.author.id, game[1], price, userdata[3]))
                    currency = {"euro": "€", "dollar": "$", "pound": "£"}
                    await ctx.send(f"Added alert for game `{game[1]}` with price <{currency[userdata[2]]}`{price}`")
            else:
                await ctx.send("Game couldn't be found in our database, please contact us on our support server.")

        # Not a steam link, searching using IGDB
        elif pricecheck:
            # Else use IGDB
            try:
                byte_array = self.wrapper.api_request(
                    'games',
                    'fields name, alternative_names.*, external_games.uid, external_games.category; limit 10; where external_games.category = 1; search "{}";'.format(
                        game)
                )
            except TypeError:
                await ctx.send("API outputted None")
                return
            data = json.loads(byte_array)
            log.info(data)

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

                async def callback(interaction, price):
                    for choice in range(0, 11):
                        if interaction.user.id == ctx.author.id:
                            if select.values[CHOICE] == str(choice):
                                # Defer interaction earlier, so it does not expire before processing has finished
                                await interaction.response.defer()
                                game = await check_game_in_db(data[choice - 1])
                                if game is None:
                                    await ctx.send("We were unable to find the game on our end. Please contact us if "
                                                   "the game exists on Steam. As for DLCs, we kindly request a "
                                                   "Steam URL.")
                                else:
                                    userdata = await sql.fetchone("SELECT * FROM user_cnf WHERE userid = %s",
                                                                  ctx.author.id)
                                    if userdata[3] == 0:
                                        max = 10
                                    elif userdata[3] == 1:
                                        max = 20

                                    if len(await sql.fetchall("SELECT * FROM alerts WHERE userid = %s",
                                                              ctx.author.id)) > (max - 1):
                                        await ctx.send("*Error*: Max alerts reached")
                                    else:
                                        price = price.replace(',', '.')
                                        if '.' not in price:
                                            price += '.00'
                                        await sql.execute(
                                            "INSERT INTO alerts (userid, game, price, premium) VALUES (%s, %s, %s, %s)",
                                            (ctx.author.id, game[1], price, userdata[3]))
                                        currency = {"euro": "€", "dollar": "$", "pound": "£"}
                                        await ctx.send(
                                            f"Added alert for game `{game[1]}` with price <{currency[userdata[2]]}`{price}`")

                        else:
                            await interaction.followup.send("You are not allowed to use this command!", ephemeral=True)

                # the price variable is passed as an argument to the callback function,
                # this should resolve the "referenced before assignment" issue.
                select.callback = lambda i: callback(i, price)
                view = View()
                view.add_item(select)
                await ctx.send(embed=embed, view=view)

            # Search results one
            elif len(data) == 1:
                async with ctx.typing():
                    game = await check_game_in_db(data[0])
                    if game is None:
                        await ctx.send("We were unable to find the game on our end. Please contact us if "
                                       "the game exists on Steam. As for DLCs, we kindly request a "
                                       "Steam URL.")
                    else:
                        userdata = await sql.fetchone("SELECT * FROM user_cnf WHERE userid = %s", ctx.author.id)
                        if userdata[3] == 0:
                            max = 10
                        elif userdata[3] == 1:
                            max = 20

                        if len(await sql.fetchall("SELECT * FROM alerts WHERE userid = %s", ctx.author.id)) > (max - 1):
                            await ctx.send("*Error*: Max alerts reached")
                        else:
                            price = price.replace(',', '.')
                            if '.' not in price:
                                price += '.00'
                            await sql.execute(
                                "INSERT INTO alerts (userid, game, price, premium) VALUES (%s, %s, %s, %s)",
                                (ctx.author.id, game[1], price, userdata[3]))
                            currency = {"euro": "€", "dollar": "$", "pound": "£"}
                            await ctx.send(
                                f"Added alert for game `{game[1]}` with price <{currency[userdata[2]]}`{price}`")
            else:
                await ctx.send(f"We were unable to locate a game or DLC titled `{game}`. If this is an error, kindly "
                               f"provide us with a Steam link or inform us of the issue.",
                               view=SupportView(game, self.bot))

        elif linkcheck[0] is False:
            await ctx.send("**Error**: Game parameter invalid")
        elif pricecheck is False:
            await ctx.send("**Error**: Price is invalid")

    @alert.command(
        description="Removes alert: alert remove <id> (id found in alert show)",
    )
    async def remove(self, ctx, id: int):
        alerts = await sql.fetchall("SELECT * FROM alerts WHERE userid = %s", ctx.author.id)
        await sql.execute("DELETE FROM alerts WHERE userid = %s AND game = %s AND price = %s LIMIT 1",
                          (alerts[id - 1][0], alerts[id - 1][1], alerts[id - 1][2]))
        await ctx.send(f"Successfully removed alert with name `{alerts[id - 1][1]}` and price `{alerts[id - 1][2]}`")

    # (game_name, game_id, args, store, user_cnf)

    @tasks.loop(time=check_alerts_time)
    async def check_alerts_basic(self):
        channel = self.bot.get_channel(772579930164035654)
        await channel.send("**LOG** Daily schedule checking alerts (basic) - STARTING")

        data = sql.fetchall("SELECT * FROM alerts WHERE premium = 0")

        await channel.send("**LOG** Daily schedule checking alerts (basic) - DONE")
        # for alert in data:

    @check_alerts_basic.before_loop
    async def before_check_alerts_basic(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(1)

    @tasks.loop(time=check_alerts_time)
    async def check_alerts_premium(self):
        log.info("start looping through alerts (premium)")

    @check_alerts_premium.before_loop
    async def before_check_alerts_premium(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(1)


async def setup(bot):
    await bot.add_cog(Pricewatch(bot))

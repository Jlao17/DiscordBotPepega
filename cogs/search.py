import discord
import requests
import json
from bot import config
from igdb.wrapper import IGDBWrapper
from discord.ext import commands
from discord.ui import View, Select
from functions.get_steam_price import get_steam_price
from functions.get_steam_game import get_steam_game
from functions.check_game_in_db import check_game_in_db
from functions.get_stores_functions.get_g2a import get_g2a as g2a
from functions.get_stores_functions.get_kinguin import get_kinguin as kinguin
from functions.get_stores_functions.get_k4g import get_k4g as k4g
from functions.get_stores_functions.get_eneba import get_eneba as eneba
from functions.get_stores_functions.get_fanatical import get_fanatical as fanatical
from functions.update_steamdb_game import update_steamdb_game
from functions.check_steamlink import check_steamlink
from components.views.SupportView import SupportView
from components.views.StoreView import StoreView

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

class Search(commands.Cog, name="search"):
    def __init__(self, bot):
        self.bot = bot
        self.wrapper = IGDBWrapper(config["igdbclient"], config["igdbaccess"])
        self.steam_apps = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2").json()
        self.browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
        }
        self.stores = {g2a: "G2A", k4g: "K4G", kinguin: "Kinguin", eneba: "Eneba", fanatical: "Fanatical"}

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

        async def get_game(args):
            result = await check_game_in_db(args)
            if isinstance(args, int):
                args = {"name": result[GAME_NAME]}
            check = 0
            # If the game cannot be found in db, exit the search command
            if result is None:
                get_game.error_message = "We were unable to find the game on our end. Please contact " \
                                         "us if the game exists on Steam. As for DLCs, we kindly request a Steam URL."
                return None, None, None, None

            # Check for 1st update db
            elif result[LAST_UPDATED] is None or int(time.time()) - int(result[LAST_UPDATED]) > 43200:
                log.info("First update or longer than 12 hours - SteamDB")
                game_data, app_name = get_steam_game(result[APP_ID])
                if game_data is None:
                    get_game.error_message = "The game is no longer extant on the Steam platform. If this is an " \
                                             "error, kindly notify us via our support server."
                    return None, None, None, None
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
            for store in self.stores:
                retrieve = await store(result[GAME_NAME], result[GAME_NAME], result[DB_ID], args, self.stores.get(store))
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
                    prices_embed.add_field(
                        name="{} - €{}".format(self.stores.get(store), price_lists[count][0][3]),
                        value="[{name}]({url})".format(name=price_lists[count][0][1], url=price_lists[count][0][2])
                    )
                count += 1

            if check == 0:
                return get_steam_price(game_data, prices_embed, result[APP_ID]), price_lists
            else:
                return get_steam_price(game_data, prices_embed, result[APP_ID], check=1), price_lists

        async def print_game(choice, interaction=None):
            loading_embed = discord.Embed(
                title="Retrieving information...",
                color=0x9C84EF
            )
            loading_embed.set_image(
                url="https://cdn.discordapp.com/attachments/421360319965822986/1105581766208655541/9a81c800a29d2516c25cbfa63b21710f.gif")
            load_msg = await ctx.send(embed=loading_embed)
            check_name, price_lists = await get_game(choice)

            store_data = []
            x = 0
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
                        await ctx.send(embed=check_name, view=StoreView(store_data))
                else:
                    if not any(price_lists):
                        await interaction.followup.send(embed=check_name)
                    else:
                        await interaction.followup.send(embed=check_name, view=StoreView(store_data))

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


async def setup(bot):
    await bot.add_cog(Search(bot))

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
from functions.get_stores_functions.get_g2a import get_g2a
from functions.get_stores_functions.get_kinguin import get_kinguin
from functions.get_stores_functions.get_k4g import get_k4g
from functions.update_steamdb_game import update_steamdb_game
from functions.check_steamlink import check_steamlink
import time


def list_to_embed(data, name):
    if data:
        prices_embed = discord.Embed(
            title="Price information {}".format(name),
            description=data[0][0],
            color=0x9C84EF
        )
        if len(data) > 1:
            for info in data:
                prices_embed.add_field(
                    name="€{price}".format(price=info[3]),
                    value="[{name}]({url})".format(name=info[1], url=info[2])
                )
        else:
            prices_embed.add_field(
                name="€{price}".format(price=data[0][3]),
                value="[{name}]({url})".format(name=data[0][1], url=data[0][2])
            )
        return prices_embed
    else:
        return None


class StoreButton(discord.ui.Button):
    def __init__(self, label, style, data, button_row):
        super().__init__(style=style, label=label)
        self.data = data
        self.button_row = button_row

    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        for button in self.button_row.children:
            if button.label != self.label:
                button.disabled = False
        embed = list_to_embed(self.data, self.label)
        await interaction.response.defer()
        await interaction.message.edit(embed=embed, view=self.button_row)


class ButtonEmbed(discord.ui.View):
    def __init__(self, g2a_data, k4g_data, kinguin_data):
        super(ButtonEmbed, self).__init__(timeout=100)
        self.g2a = g2a_data
        self.k4g = k4g_data
        self.kinguin = kinguin_data

        if self.g2a:
            self.add_item(StoreButton("G2A", discord.ButtonStyle.danger, self.g2a, self))
        if self.k4g:
            self.add_item(StoreButton("K4G", discord.ButtonStyle.danger, self.k4g, self))
        if self.kinguin:
            self.add_item(StoreButton("Kinguin", discord.ButtonStyle.danger, self.kinguin, self))


class SupportButton(discord.ui.View):
    def __init__(self, args, bot):
        super(SupportButton, self).__init__(timeout=30)
        self.args = args
        self.bot = bot

    @discord.ui.button(label='Report', style=discord.ButtonStyle.green)
    async def report(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("I've reported this to support, head over to our support server for updates")
        channel = self.bot.get_channel(772579930164035654)
        await channel.send(f"**LOG** - User reported non-existing game/dlc in IGDB/db: `{self.args}`")

    @discord.ui.button(label='Support', style=discord.ButtonStyle.blurple)
    async def support(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(">Support server link here<")


class Search(commands.Cog, name="search"):
    def __init__(self, bot):
        self.bot = bot
        self.wrapper = IGDBWrapper(config["igdbclient"], config["igdbaccess"])
        self.steam_apps = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2").json()
        self.browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
        }

    @commands.hybrid_command(
        name="search",
        description="Search for games",
    )
    async def search(self, ctx, *, args: str):
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
                    'fields name, alternative_names.*; limit 10; where category = (0,8,9); search "{}";'.format(args)
                )
            except TypeError:
                await ctx.send("API outputted None")
                return
            data = json.loads(byte_array)
            print(data)

        async def get_game(args):
            result = await check_game_in_db(args)
            check = 0
            # If the game cannot be found in db, exit the search command
            if result is None:
                get_game.error_message = "We were unable to find the game on our end. Please contact " \
                                         "us if the game exists on Steam. As for DLCs, we kindly request a Steam URL."
                return None, None, None, None

            # Check for 1st update db
            elif result[10] is None or int(time.time()) - int(result[10]) > 43200:
                print("First update or longer than 12 hours - SteamDB")
                game_data, app_name = get_steam_game(result[2])
                if game_data is None:
                    get_game.error_message = "The game is no longer extant on the Steam platform. If this is an " \
                                             "error, kindly notify us via our support server."
                    return None, None, None, None
                await update_steamdb_game(game_data, result[2])
            else:
                print("Less than 12 hours - SteamDB")
                # Use the current data in db
                check = 1
                game_data = [f"€{(int(result[5]) / 100):.2f}", result[3]]

            # You see 2 result[1]. It used to be game_name and app_name
            # to combat steam appdetails game name difference, might fix later
            price_list_g2a = await get_g2a(result[1], result[1], result[0])
            print("G2A list:", price_list_g2a)

            price_list_k4g = await get_k4g(result[1], result[1], result[0])
            print("K4G list:", price_list_k4g)

            price_list_kinguin = await get_kinguin(result[1], result[1], result[0])
            print("Kinguin list:", price_list_kinguin)

            price_list_g2a.sort(key=lambda x: 0 if x[3] == '' else float(x[3]))
            price_list_k4g.sort(key=lambda x: 0 if x[3] == '' else float(x[3]))
            price_list_kinguin.sort(key=lambda x: 0 if x[3] == '' else float(x[3]))

            prices_embed = discord.Embed(
                title="Price information",
                description=result[1],
                color=0x9C84EF
            )
            if price_list_g2a:
                prices_embed.add_field(
                    name="G2A - €{price}".format(price=price_list_g2a[0][3]),
                    value="[{name}]({url})".format(name=price_list_g2a[0][1], url=price_list_g2a[0][2])
                )
            if price_list_k4g:
                prices_embed.add_field(
                    name="K4G - €{price}".format(price=price_list_k4g[0][3]),
                    value="[{name}]({url})".format(name=price_list_k4g[0][1], url=price_list_k4g[0][2])
                )
            if price_list_kinguin:
                prices_embed.add_field(
                    name="Kinguin - €{price}".format(price=price_list_kinguin[0][3]),
                    value="[{name}]({url})".format(name=price_list_kinguin[0][1], url=price_list_kinguin[0][2])
                )

            if check == 0:
                return get_steam_price(game_data, prices_embed, result[2]), \
                       price_list_g2a, \
                       price_list_k4g, \
                       price_list_kinguin
            else:
                return get_steam_price(game_data, prices_embed, result[2], check=1), \
                       price_list_g2a, \
                       price_list_k4g, \
                       price_list_kinguin

        async def print_game(choice, interaction=None):
            check_name, price_list_g2a, price_list_k4g, price_list_kinguin = await get_game(choice)
            if check_name is None:
                await ctx.send(get_game.error_message)
            else:
                if interaction is None:
                    await ctx.send(embed=check_name, view=ButtonEmbed(price_list_g2a,
                                                                      price_list_k4g,
                                                                      price_list_kinguin))
                else:
                    await interaction.followup.send(embed=check_name, view=ButtonEmbed(price_list_g2a,
                                                                                       price_list_k4g,
                                                                                       price_list_kinguin))

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
                    if select.values[0] == str(choice):
                        async with ctx.typing():
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
                           view=SupportButton(args, self.bot))


async def setup(bot):
    await bot.add_cog(Search(bot))

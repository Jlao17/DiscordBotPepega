import platform
import string
import discord
import requests
import json
from bot import config
from igdb.wrapper import IGDBWrapper
from discord.ext import commands
from discord.ui import View, Select
asciiAndNumbers = string.ascii_letters + string.digits


class Search(commands.Cog, name="search"):
    def __init__(self, bot):
        self.bot = bot
        self.wrapper = IGDBWrapper(config["igdbclient"], config["igdbaccess"])
        self.steam_apps = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2").json()

    @commands.hybrid_command(
        name="search",
        description="Search for games",
    )
    async def search(self, ctx, *, args: str):
        """https://api-docs.igdb.com/#about"""
        byte_array = self.wrapper.api_request(
            'games',
            'fields name, alternative_names.*; limit 10; where category = (0,8,9); search "{}";'.format(args)
        )
        data = json.loads(byte_array)
        # Mimic browser API request
        g2a_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
        }
        print(json.dumps(data, indent=4))

        def normalizedtext(text):
            # We are just allowing a-z, A-Z and 0-9 and use lowercase characters
            return ''.join(c for c in text if c in asciiAndNumbers).lower()

        def get_game(args):
            game_appid = None
            prices_embed = discord.Embed(
                title="Price information",
                description=args,
                color=0x9C84EF
            )
            print("args: " + args)
            for app in self.steam_apps["applist"]["apps"]:
                if normalizedtext(app["name"].lower()) == normalizedtext(args.lower()):
                    print("found it")
                    game_appid = str(app["appid"])
                    print("appid:" + game_appid)
                    break
            if game_appid is None:
                print("game not found")
                return

            game_json_steam = requests.get(
                "http://store.steampowered.com/api/appdetails?appids=" + game_appid
            ).json()
            game_data = game_json_steam[game_appid]["data"]
            game_name = game_data["name"]
            game_json_g2a = requests.get(
                "https://www.g2a.com/search/api/v2/products?itemsPerPage=4&"
                "include[0]=filters&currency=EUR&isWholesale=false&category=1&"
                "f[regions][0]=8355&f[device][0]=1118&phrase=" + game_name, headers=g2a_headers
            ).json()
            for g2a_app in game_json_g2a["data"]["items"]:
                print(g2a_app)
                g2a_app_url = "https://www.g2a.com" + g2a_app["href"]
                g2a_app_price = g2a_app["price"] + g2a_app["currency"]
                g2a_app_name = g2a_app["name"]
                embed_name = g2a_app_name + " - " + g2a_app_price
                prices_embed.add_field(
                    name="G2A - {price}".format(price=g2a_app_price),
                    value="[{name}]({url})".format(name=embed_name, url=g2a_app_url)
                )
            print("out loop")

            if "price_overview" not in game_data:
                print("key not found")
                price_total = game_name + ": Free"
            else:
                price = game_data["price_overview"]
                price_currency = price["currency"]
                print(price_currency)
                price_final = price["final"]
                print(price_final)
                # name_and_price = game_name + ": " + str(price_final / 100) + price_currency
                price_total = str(price_final / 100) + price_currency
            # price_discount = price["discount_percent"]
            prices_embed.add_field(name="Steam - " + price_total, value="Link here")
            prices_embed.set_thumbnail(url=game_data["header_image"])
            print("reached steam end")
            return prices_embed

        async def print_game(choice, interaction=None):
            check_name = get_game(choice["name"])
            if check_name is None:
                for alt_name in choice["alternative_names"]:
                    check_name = get_game(alt_name["name"])
            if check_name is None:
                if interaction is None:
                    await ctx.send("Game could not be found on Steam.")
                else:
                    await interaction.response.send_message("Game could not be found on Steam.")
            else:
                if interaction is None:
                    await ctx.send(embed=check_name)
                else:
                    await interaction.response.send_message(embed=check_name)

        # Search results 0
        if len(data) < 1:
            await ctx.send("I've found no game")
        # Search results more than 1
        elif len(data) > 1:
            x = 1
            game_list = []
            for game in data:
                game_list.append(discord.SelectOption(label=game["name"], value="{}".format(x)))
                x += 1
            embed = discord.Embed(title="Select game", description="")
            select = Select(
                placeholder="Select a game",
                options=game_list
            )

            async def callback(interaction):
                for choice in range(0, 11):
                    if select.values[0] == str(choice):
                        choice_data = data[choice]
                        async with ctx.typing():
                            await print_game(choice_data, interaction)

            select.callback = callback
            view = View()
            view.add_item(select)
            await ctx.send(embed=embed, view=view)
        # Search results one
        else:
            async with ctx.typing():
                await print_game(data[0])

        # Output price for that one game
        # To do:    1. dropdown list if more than one game in list
        #           2. Output prices for selected game


async def setup(bot):
    await bot.add_cog(Search(bot))

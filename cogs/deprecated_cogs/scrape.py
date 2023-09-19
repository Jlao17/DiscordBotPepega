import platform

import discord
import requests
import json
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import View, Select
from igdb.wrapper import IGDBWrapper

from bot import config


class Scrape(commands.Cog, name="scrape"):
    def __init__(self, bot):
        self.bot = bot
        self.wrapper = IGDBWrapper(config["igdbclient"], config["igdbaccess"])

    @commands.hybrid_command(
        name="scrape",
        description="webscraper",
    )
    async def scrape(self, ctx, *, args: str):
        """https://api-docs.igdb.com/#about"""
        byte_array = self.wrapper.api_request(
            'games',
            'fields name, alternative_names.*; limit 10; where category = (0,8,9); search "{}";'.format(args)
        )

        cookies = {
            'awch': 'www.allkeyshop.com',
            '_gcl_au': '1.1.286038486.1669588164',
            'gaVisitorUuid': 'bc730215-4e16-45d3-bb53-c42fce1c8aff',
            'gaIsValuable': '1',
            '_ga': 'GA1.2.79261740.1669588172',
            'gmvLang': 'en',
            'gaNotificationConsent': 'rejected',
            'ravelinDeviceId': 'rjs-f9dc3a4d-7d3d-4459-b73b-37a0e96b38c4',
            '_gid': 'GA1.2.1171804094.1672393131',
            '__cf_bm': 'PkI3yDQwWCYOYm0GkNkLTiuRY9jZg1hU07E6NQzvY1M-1672410220-0-ASHc/KNIOVpv3bH7X1XpPb2QMU+Dsylxotr5Mt4v4CybEzFC4ifjIVc+dlXb/LivhVTNfwiRPSdKz5AE4HDcltyEamA/LJnjX7xsQvWiI2TCLwFy191COD8xdhByFhYOC4yMQe6uql1AbiUZThjbeJie/uh8nFgDPmZRsF2QZGFbAxFIgTz6ZN19/78SkUIIJsqQ59S15cSDY/ojzMHLdnQ=',
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Connection': 'keep-alive',
            'Cookie': 'awch=www.allkeyshop.com; _gcl_au=1.1.286038486.1669588164; gaVisitorUuid=bc730215-4e16-45d3-bb53-c42fce1c8aff; gaIsValuable=1; _ga=GA1.2.79261740.1669588172; gmvLang=en; gaNotificationConsent=rejected; ravelinDeviceId=rjs-f9dc3a4d-7d3d-4459-b73b-37a0e96b38c4; _gid=GA1.2.1171804094.1672393131; __cf_bm=PkI3yDQwWCYOYm0GkNkLTiuRY9jZg1hU07E6NQzvY1M-1672410220-0-ASHc/KNIOVpv3bH7X1XpPb2QMU+Dsylxotr5Mt4v4CybEzFC4ifjIVc+dlXb/LivhVTNfwiRPSdKz5AE4HDcltyEamA/LJnjX7xsQvWiI2TCLwFy191COD8xdhByFhYOC4yMQe6uql1AbiUZThjbeJie/uh8nFgDPmZRsF2QZGFbAxFIgTz6ZN19/78SkUIIJsqQ59S15cSDY/ojzMHLdnQ=',
        }

        params = {
            'regions': '["Global"]',
            'languages': '["English"]',
        }

        data = json.loads(byte_array)
        # Mimic browser API request
        print(json.dumps(data, indent=4))

        async def web_scrape(data):
            name = data["name"]
            print("got name")
            url = "https://www.gamivo.com/search/" + name
            print("got url")
            page = requests.get(url, params=params, cookies=cookies, headers=headers)
            print("got page")
            # soup = BeautifulSoup(page.content, "html.parser", from_encoding="iso-8859-1")
            # print(soup)
            # results = soup.find_all("a", attrs={"class": "product-tile--link ng-star-inserted"})

            # print(results.prettify())

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
                        choice_data = data[choice - 1]
                        async with ctx.typing():
                            await web_scrape(choice_data)

            select.callback = callback
            view = View()
            view.add_item(select)
            await ctx.send(embed=embed, view=view)
        # Search results one
        else:
            async with ctx.typing():
                await ctx.send("one game found")

        # Output price for that one game
        # To do:    1. dropdown list if more than one game in list
        #           2. Output prices for selected game


async def setup(bot):
    await bot.add_cog(Scrape(bot))

import platform

import discord
import requests
import json
from discord.ext import commands
from discord.ext.commands import Context
from bot import config


class Search(commands.Cog, name="search"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="search",
        description="Get some useful (or not) information about the bot.",
    )
    async def search(self, context: Context, *, args: str):
        """
        Search for games on steam using the following link format:
        http://api.steampowered.com/<interface name>/<method name>/v<version>/?key=<api key>&format=<format>

        :param context: The hybrid command context.
        :param args: The game to be searched.
        """

        args = args.lower()
        api_key = config["steam_api"]
        interface = "IStoreService"
        method = "GetAppList"
        version = "v1"

        # responses = requests.get("http://api.steampowered.com/" +
        #                          interface + "/" + method + "/" + version + "/?key=" + api_key)

        steam_apps = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2").json()

        def get_game_id():
            game_id = ""
            for app in steam_apps["applist"]["apps"]:
                if app["name"].lower() == args:
                    game_id = app["appid"]
            return str(game_id)

        game_appid = get_game_id()
        game_json = requests.get("http://store.steampowered.com/api/appdetails?appids=" + game_appid).json()

        game = game_json[game_appid]["data"]
        game_name = game["name"]
        game_description = game["short_description"]
        game_thumbnail = game["header_image"]

        print(get_game_id())
        print(json.dumps(game, indent=4))

        embed = discord.Embed(
            title=game_name,
            description=f"{game_description}",
            color=0x9C84EF
        )
        embed.set_thumbnail(url=game_thumbnail)

        await context.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Search(bot))

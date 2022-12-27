import platform

import discord
import requests
import json
from discord.ext import commands
from discord.ext.commands import Context
from bot import config
from helpers.db_connect import startsql as sql


class steam(commands.Cog, name="steam"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="steam",
        description="steam",
    )
    async def steam(self, ctx: Context):\

        steam_api = config["steam_api"]

        # headers = {
        #     "Authorization": client_id + ", " + api_key
        # }


        steam = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/?format=json").json()
        print(steam)

async def setup(bot):
    await bot.add_cog(steam(bot))
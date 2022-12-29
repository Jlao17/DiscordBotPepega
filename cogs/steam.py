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
        name="compare",
        description="compare",
    )
    async def compare(self, ctx, *, args: str):
        stri = "Hermes: War of the Gods - Steam - Key GLOBAL"
        if args in stri:
            await ctx.send("{} is in {}".format(args, stri))
        else:
            await ctx.send("{} is not in {}".format(args, stri))


async def setup(bot):
    await bot.add_cog(steam(bot))
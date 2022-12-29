import platform

import discord
import requests
import json
from discord.ext import commands
from discord.ext.commands import Context
from bot import config
from helpers.db_connect import startsql as sql
import re


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

    @commands.hybrid_command(
        name="test",
        description="compare",
    )
    async def test(self, ctx, game_name, vendor_name):
        trigger_words = ["remake", "remade", "remaster", "remastered"]
        # Check eerst of de trigger woord al in de searched naam zit en dan ook in vendor_naam
        for word in trigger_words:
            print(word)
            if re.search(r'\b' + word + r'\b', game_name):
                for word2 in trigger_words:
                    if re.search(r'\b' + word2 + r'\b', vendor_name):
                        return await ctx.send("FOUND ON BOTH ENDS")
                return await ctx.send("FOUND FIRST ONLY")
        return await ctx.send("FOUND NOPES")

async def setup(bot):
    await bot.add_cog(steam(bot))
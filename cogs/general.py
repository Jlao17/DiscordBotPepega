""""
Copyright © Krypton 2022 - https://github.com/kkrypt0nn (https://krypton.ninja)
Description:
This is a template to create your own discord bot in python.

Version: 5.1
"""

import platform
import random
import ssl
import certifi
import requests
from typing import Literal
import aiohttp
import discord
import logging
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
from helpers.db_connectv2 import startsql as sql

log = logging.getLogger(__name__)


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="help",
        description="List all commands the bot has loaded."
    )
    async def help(self, context: Context) -> None:
        prefix = self.bot.config["prefix"]
        embed = discord.Embed(title="Help", description="List of available commands:", color=0x9C84EF)
        for i in self.bot.cogs:
            print(i)
            try:
                cog = self.bot.get_cog(i.lower())
                log.info(cog)
                commands = cog.get_commands()
                data = []
                for command in commands:
                    description = command.description.partition('\n')[0]
                    data.append(f"{prefix}{command.name} - {description}")
                help_text = "\n".join(data)
                embed.add_field(name=i.capitalize(), value=f'```{help_text}```', inline=False)
            except:
                pass
        user = await sql.fetchone("SELECT * FROM user_cnf WHERE userid = %s", context.author.id)
        if user is None:
            log.info("no")
            user = await sql.execute("INSERT INTO user_cnf (userid) VALUES (%s)", context.author.id)
        try:
            if user[4] == 1:
                log.info("ON")
                embed.set_footer(text="tip: to disable DMs use the command dms off")
                await context.message.author.send(embed=embed)
                await context.send("I've sent a DM to you!", delete_after=5)
            else:
                log.info("OFF")
                embed.set_footer(text="tip: to enable DMs use the command dms on")
                await context.send(embed=embed)
        except:
            embed.set_footer(text="tip: make sure to enable dms to avoid clogging the channel!")
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="dms",
        description="Turn DMs on or off"
    )
    async def dms(self, ctx: Context, dms: Literal["off", "on"]) -> None:
        if await sql.fetchone("SELECT * FROM user_cnf WHERE userid = %s", ctx.author.id) is None:
            log.info("no")
            await sql.execute("INSERT INTO user_cnf (userid) VALUES (%s)", ctx.author.id)
        if dms.lower() not in ["on", "off"]:
            await ctx.send("[**Error**] Please select `on` or `off`")
            return
        if dms.lower() == "on":
            await sql.execute("UPDATE user_cnf SET dms = %s WHERE userid = %s", (1, ctx.author.id))
            await ctx.send(f"You've turned on DMs")
        elif dms.lower() == "off":
            await sql.execute("UPDATE user_cnf SET dms = %s WHERE userid = %s", (0, ctx.author.id))
            await ctx.send(f"You've turned off DMs")


    @commands.hybrid_command(
        name="botinfo",
        description="Get some useful (or not) information about the bot.",
    )
    async def botinfo(self, context: Context) -> None:
        """
        Get some useful (or not) information about the bot.
        
        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            description="Bot for price watch of games",
            color=0x9C84EF
        )
        embed.set_author(
            name="Bot Information"
        )
        embed.add_field(
            name="Owners:",
            value="DarkSide#1111 - Dogege#3905",
            inline=True
        )
        embed.add_field(
            name="Python Version:",
            value=f"{platform.python_version()}",
            inline=True
        )
        embed.add_field(
            name="Prefix:",
            value=f"/ (Slash Commands) or {self.bot.config['prefix']} for normal commands",
            inline=False
        )
        embed.set_footer(
            text=f"Requested by {context.author}"
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="serverinfo",
        description="Get some useful (or not) information about the server.",
    )
    async def serverinfo(self, context: Context) -> None:
        """
        Get some useful (or not) information about the server.
        
        :param context: The hybrid command context.
        """
        roles = [role.name for role in context.guild.roles]
        if len(roles) > 50:
            roles = roles[:50]
            roles.append(f">>>> Displaying[50/{len(roles)}] Roles")
        roles = ", ".join(roles)

        embed = discord.Embed(
            title="**Server Name:**",
            description=f"{context.guild}",
            color=0x9C84EF
        )
        if context.guild.icon is not None:
            embed.set_thumbnail(
                url=context.guild.icon.url
            )
        embed.add_field(
            name="Server ID",
            value=context.guild.id
        )
        embed.add_field(
            name="Member Count",
            value=context.guild.member_count
        )
        embed.add_field(
            name="Text/Voice Channels",
            value=f"{len(context.guild.channels)}"
        )
        embed.add_field(
            name=f"Roles ({len(context.guild.roles)})",
            value=roles
        )
        embed.set_footer(
            text=f"Created at: {context.guild.created_at}"
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="ping",
        description="Check if the bot is alive.",
    )
    async def ping(self, context: Context) -> None:
        """
        Check if the bot is alive.
        
        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=0x9C84EF
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="invite",
        description="Get the invite link of the bot to be able to invite it.",
    )
    async def invite(self, context: Context) -> None:
        """
        Get the invite link of the bot to be able to invite it.
        
        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            description=f"Invite me by clicking [here](https://discordapp.com/oauth2/authorize?&client_id={self.bot.config['application_id']}&scope=bot+applications.commands&permissions={self.bot.config['permissions']}).",
            color=0xD75BF4
        )
        try:
            # To know what permissions to give to your bot, please see here: https://discordapi.com/permissions.html and remember to not give Administrator permissions.
            await context.author.send(embed=embed)
            await context.send("I sent you a private message!")
        except discord.Forbidden:
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="server",
        description="Get the invite link of the discord server of the bot for some support.",
    )
    async def server(self, context: Context) -> None:
        """
        Get the invite link of the discord server of the bot for some support.
        
        :param context: The hybrid command context.
        """
        embed = discord.Embed(
            description=f"Join the support server for the bot by clicking [here](https://discord.gg/cjZCZCX).",
            color=0xD75BF4
        )
        try:
            await context.author.send(embed=embed)
            await context.send("I sent you a private message!")
        except discord.Forbidden:
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="8ball",
        description="Ask any question to the bot.",
    )
    @app_commands.describe(question="The question you want to ask.")
    async def eight_ball(self, context: Context, *, question: str) -> None:
        """
        Ask any question to the bot.
        
        :param context: The hybrid command context.
        :param question: The question that should be asked by the user.
        """
        answers = ["It is certain.", "It is decidedly so.", "You may rely on it.", "Without a doubt.",
                   "Yes - definitely.", "As I see, yes.", "Most likely.", "Outlook good.", "Yes.",
                   "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
                   "Cannot predict now.", "Concentrate and ask again later.", "Don't count on it.", "My reply is no.",
                   "My sources say no.", "Outlook not so good.", "Very doubtful."]
        embed = discord.Embed(
            title="**My Answer:**",
            description=f"{random.choice(answers)}",
            color=0x9C84EF
        )
        embed.set_footer(
            text=f"The question was: {question}"
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="bitcoin",
        description="Get the current price of bitcoin.",
    )
    async def bitcoin(self, context: Context) -> None:
        """
        Get the current price of bitcoin.
        
        :param context: The hybrid command context.
        """
        # This will prevent your bot from stopping everything when doing a web request - see: https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-make-a-web-request
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.coindesk.com/v1/bpi/currentprice/BTC.json") as request:
                if request.status == 200:
                    data = await request.json(
                        content_type="application/javascript")  # For some reason the returned content is of type JavaScript
                    embed = discord.Embed(
                        title="Bitcoin price",
                        description=f"The current price is {data['bpi']['USD']['rate']} :dollar:",
                        color=0x9C84EF
                    )
                else:
                    embed = discord.Embed(
                        title="Error!",
                        description="There is something wrong with the API, please try again later",
                        color=0xE02B2B
                    )
                await context.send(embed=embed)

    # @commands.hybrid_command(
    #     name="test",
    #     description="testdb",
    # )
    # async def test(self, context: Context, test) -> None:
    #     # Change region and game/dlc in the link, params won't work
    #     url = "https://search.driffle.com/products/v2/list?limit=10&productType=game&region[]=1&region[]=3&region[]=18&page=1&q={}&worksOn[]=windows".format(
    #         test.replace(" ", "+"))
    #     headers = {
    #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
    #     }
    #
    #     game_json = requests.request("GET", url, headers=headers)
    #
    #     print(game_json.status_code)


async def setup(bot):
    await bot.add_cog(General(bot))

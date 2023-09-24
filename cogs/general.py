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
import aiohttp
import discord
import logging
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

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
        try:
            await context.message.author.send(embed=embed)
            await context.send("I've sent a DM to you!", delete_after=5)
        except:
            await context.send(embed=embed)
            await context.send("tip: Make sure to *enable* DMs to avoid clogging the channel")

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

    @commands.hybrid_command(
        name="testt",
        description="test",
    )
    async def testt(self, context: Context) -> None:
        proxy = {
            "http": "http://190.58.248.86:80",
        }
        url = "https://www.g2a.com/search/api/v2/products"
        cookies = {
            '_abck': '6049BB7992C323BC33F366D8E5F0675F~0~YAAQBkd7XD3eDI+KAQAAdSP/xQqkxgCRxpmgpX6AH6JUSiNJ3y2dA/1vxFL68R3rtqShsS8+PQviaJOO7k4faJ06wyRbjDGfF0QDA3rjKbp1XdhB34L7QRqrhc98cvHzyQ5Gi7AQOBenaL3tfMaA93vsHNL0w9IP06964EVGYpUe5xcrFArIq/zMzkZKhd/6De0ADhfgv8cAYvl+fWMS+RbMxHUpukEITdL4x/uB2JdjDgH0/XuJvM0MKYI+wu/QHwPXSaPrkV2/TQR7HQOtyynWzgkXyarmqAsqRIk13eJaj9e63blxuF6WUXMGIjjhsMie7Ho+rX6OI4bdvZ07T/hlnGrvDeN0lAHHjKV3LZ4UhUAXAKME7kXL6wm0cFtrdw+MnBXIxlJGC5wjQlOC64igDkQ/Vw==~-1~^|^|-1^|^|~-1',
            'skc': '0a41d3e3-c763-411c-9ea6-3d46b8cf2065-1672008851',
            'currency': 'USD',
            'store': 'englishus',
            'fingerprint': 'c5bf386dfcc6453a803bced8e94a3cf3',
            'quickAccessType': 'google',
            'language': 'en',
            'null-avatar_id': 'https^%^3A^%^2F^%^2Fstatic.g2a.com^%^2FxAsiiuY6oKCFifTi59qELP^%^2Favatar_5.svg',
            'g_state': '{i_l:0}',
            'gdpr_cookie': '^%^5B^%^22COOKIE-1-1^%^22^%^2C^%^22COOKIE-2-1^%^22^%^2C^%^22COOKIE-3-1^%^22^%^5D',
            'recently_viewed': '^%^5B^%^2210000191594001^%^22^%^2C^%^2210000305987002^%^22^%^2C^%^2210000337681001^%^22^%^2C^%^2210000084545004^%^22^%^2C^%^2210000196111021^%^22^%^2C^%^2210000336729001^%^22^%^5D',
            '_snrs_p': 'host:www.g2a.com&permUuid:9d7e1ad8-5ca1-4964-8366-2346f8b6f7b6&uuid:9d7e1ad8-5ca1-4964-8366-2346f8b6f7b6&identityHash:&user_hash:&init:1690668621&last:1695317247.972&current:1695317248&uniqueVisits:2&allVisits:2',
            '_snrs_uuid': '9d7e1ad8-5ca1-4964-8366-2346f8b6f7b6',
            '_snrs_puuid': '9d7e1ad8-5ca1-4964-8366-2346f8b6f7b6',
            'affiliate_id': '601',
            'affiliate_ds': '601',
            'affiliate_adid': 'direct',
            'ak_bmsc': '7379D144E42B52BDA7959F54EDB9BB21~000000000000000000000000000000~YAAQBkd7XCy+DI+KAQAAep/6xRVIkKkK4Qzvccjy3hGcnvDEWabwVrUgSF9MgWXYHspJU2OuUrIV/nib3Asj99W2Xfb0zj277x5qjoiZeMcg4/bjTYEwTpTwOGGYvhL3Ib+q1f/XRtmilGUYilWPaOSC5Z06Iqt0d1P79koRV/F9tkL9LHSvmzsfxDw1vAsuBdi3sI921stP3qeQAOb0cIL/r7IZUrGHLWNVC2yz58BG3vILVqQJN7spFX1jPbr1QXJNuZCldlxXtR3V33Zs4KZeG4pI1Xx8n/aA8Aqoe1LQmUr0CVWEvkpR4TC68zRLwUniS3GvVcxgoBQI7pv7YxsVXnkSl6OQ+9u5JUHriThi5Ghl/0uFcmKhTT50KrzzDEAlyrLUAw==',
            'bm_sz': '5B0998450EC3099BA15DF1E6646BBEF5~YAAQBkd7XC2+DI+KAQAAep/6xRUcdn7G00nbatHnb4kwz/duWit49auBfjzqx2J6UF4DE20v+j/bONWiHa/7Uk/ef9TzQORrz16pTncDrXjastQAeg2enhnTIHpk/RyrEzkFzBrxjmoF7xxco5vGXiaulBTUCxP/3CG+0Hiexe82V0e532sMtMcGXzIjQhmQW3cSM9MTX8inc2jUQDJt0U5En5UhoEoLxnKnpFMfd+l5yeDf8ZZ8Ul7qF/wJEzwDyora+L9s26IgZBzdS60Z/mgmicvlcyQvGcIbLwDuPMM=~4473926~3486018',
            'bm_sv': '372B049E194B3C9FF4B0073804C04685~YAAQmHzRF4SeXayKAQAAntwExhVDaBlSAFWIe1/jz6kQyaWg9q3cluPJwngAr7AeZknWcsqETtQqw2j5ArQD/ZDft163sqDPtmdCLInR1WT8vAkxiLYw0axS4He1WPWsLN6K6aA8VJWfl5gC5bztba24dKqxRBjt1cA17rvfhhVaG8ZAPPIJvx+wXNmTaqz2ZIVAZ5NUOAMby7rCKE8oDy5nQRKHBAhE+05R7AJojEYKVtcHD4Nq4uZlJzbWKw==~1',
            'bm_mi': '7695186A26951119B60BE483095DD1B6~YAAQBkd7XDjeDI+KAQAA4h7/xRXze1YWKsIGJpJcld7TgCk5RSFVs/emuDcs93qKrotj0DDCKmceZu4d0j4MGLt9La1GEdui+TC+x+BVRw+g0Gf8uxopcsmjgfH6EIlSq/w/2kFmcP19TKphJDpSVZe1+CI1aqvleU0tToP7uQSMqTzvIUktmrF+jJdw5iHUST+UMjDgtrkjqtUg+6du2TSZwNnlQEBEyZCPfpAsyUggu0iOmZjq3M5uwMgSYCt8yu3VxQSWgezP9fJUZP9oX+QxgSDoqRYd9POHR4GxZzuBzeLaswJb9EE/qn5ieIWGdoLDJo6naA==~1',
            'gtm_client_id': '3267200723.1695538944796',
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            # 'Cookie': '_abck=6049BB7992C323BC33F366D8E5F0675F~0~YAAQBkd7XD3eDI+KAQAAdSP/xQqkxgCRxpmgpX6AH6JUSiNJ3y2dA/1vxFL68R3rtqShsS8+PQviaJOO7k4faJ06wyRbjDGfF0QDA3rjKbp1XdhB34L7QRqrhc98cvHzyQ5Gi7AQOBenaL3tfMaA93vsHNL0w9IP06964EVGYpUe5xcrFArIq/zMzkZKhd/6De0ADhfgv8cAYvl+fWMS+RbMxHUpukEITdL4x/uB2JdjDgH0/XuJvM0MKYI+wu/QHwPXSaPrkV2/TQR7HQOtyynWzgkXyarmqAsqRIk13eJaj9e63blxuF6WUXMGIjjhsMie7Ho+rX6OI4bdvZ07T/hlnGrvDeN0lAHHjKV3LZ4UhUAXAKME7kXL6wm0cFtrdw+MnBXIxlJGC5wjQlOC64igDkQ/Vw==~-1~^|^|-1^|^|~-1; skc=0a41d3e3-c763-411c-9ea6-3d46b8cf2065-1672008851; currency=USD; store=englishus; fingerprint=c5bf386dfcc6453a803bced8e94a3cf3; quickAccessType=google; language=en; null-avatar_id=https^%^3A^%^2F^%^2Fstatic.g2a.com^%^2FxAsiiuY6oKCFifTi59qELP^%^2Favatar_5.svg; g_state={i_l:0}; gdpr_cookie=^%^5B^%^22COOKIE-1-1^%^22^%^2C^%^22COOKIE-2-1^%^22^%^2C^%^22COOKIE-3-1^%^22^%^5D; recently_viewed=^%^5B^%^2210000191594001^%^22^%^2C^%^2210000305987002^%^22^%^2C^%^2210000337681001^%^22^%^2C^%^2210000084545004^%^22^%^2C^%^2210000196111021^%^22^%^2C^%^2210000336729001^%^22^%^5D; _snrs_p=host:www.g2a.com&permUuid:9d7e1ad8-5ca1-4964-8366-2346f8b6f7b6&uuid:9d7e1ad8-5ca1-4964-8366-2346f8b6f7b6&identityHash:&user_hash:&init:1690668621&last:1695317247.972&current:1695317248&uniqueVisits:2&allVisits:2; _snrs_uuid=9d7e1ad8-5ca1-4964-8366-2346f8b6f7b6; _snrs_puuid=9d7e1ad8-5ca1-4964-8366-2346f8b6f7b6; affiliate_id=601; affiliate_ds=601; affiliate_adid=direct; ak_bmsc=7379D144E42B52BDA7959F54EDB9BB21~000000000000000000000000000000~YAAQBkd7XCy+DI+KAQAAep/6xRVIkKkK4Qzvccjy3hGcnvDEWabwVrUgSF9MgWXYHspJU2OuUrIV/nib3Asj99W2Xfb0zj277x5qjoiZeMcg4/bjTYEwTpTwOGGYvhL3Ib+q1f/XRtmilGUYilWPaOSC5Z06Iqt0d1P79koRV/F9tkL9LHSvmzsfxDw1vAsuBdi3sI921stP3qeQAOb0cIL/r7IZUrGHLWNVC2yz58BG3vILVqQJN7spFX1jPbr1QXJNuZCldlxXtR3V33Zs4KZeG4pI1Xx8n/aA8Aqoe1LQmUr0CVWEvkpR4TC68zRLwUniS3GvVcxgoBQI7pv7YxsVXnkSl6OQ+9u5JUHriThi5Ghl/0uFcmKhTT50KrzzDEAlyrLUAw==; bm_sz=5B0998450EC3099BA15DF1E6646BBEF5~YAAQBkd7XC2+DI+KAQAAep/6xRUcdn7G00nbatHnb4kwz/duWit49auBfjzqx2J6UF4DE20v+j/bONWiHa/7Uk/ef9TzQORrz16pTncDrXjastQAeg2enhnTIHpk/RyrEzkFzBrxjmoF7xxco5vGXiaulBTUCxP/3CG+0Hiexe82V0e532sMtMcGXzIjQhmQW3cSM9MTX8inc2jUQDJt0U5En5UhoEoLxnKnpFMfd+l5yeDf8ZZ8Ul7qF/wJEzwDyora+L9s26IgZBzdS60Z/mgmicvlcyQvGcIbLwDuPMM=~4473926~3486018; bm_sv=372B049E194B3C9FF4B0073804C04685~YAAQmHzRF4SeXayKAQAAntwExhVDaBlSAFWIe1/jz6kQyaWg9q3cluPJwngAr7AeZknWcsqETtQqw2j5ArQD/ZDft163sqDPtmdCLInR1WT8vAkxiLYw0axS4He1WPWsLN6K6aA8VJWfl5gC5bztba24dKqxRBjt1cA17rvfhhVaG8ZAPPIJvx+wXNmTaqz2ZIVAZ5NUOAMby7rCKE8oDy5nQRKHBAhE+05R7AJojEYKVtcHD4Nq4uZlJzbWKw==~1; bm_mi=7695186A26951119B60BE483095DD1B6~YAAQBkd7XDjeDI+KAQAA4h7/xRXze1YWKsIGJpJcld7TgCk5RSFVs/emuDcs93qKrotj0DDCKmceZu4d0j4MGLt9La1GEdui+TC+x+BVRw+g0Gf8uxopcsmjgfH6EIlSq/w/2kFmcP19TKphJDpSVZe1+CI1aqvleU0tToP7uQSMqTzvIUktmrF+jJdw5iHUST+UMjDgtrkjqtUg+6du2TSZwNnlQEBEyZCPfpAsyUggu0iOmZjq3M5uwMgSYCt8yu3VxQSWgezP9fJUZP9oX+QxgSDoqRYd9POHR4GxZzuBzeLaswJb9EE/qn5ieIWGdoLDJo6naA==~1; gtm_client_id=3267200723.1695538944796',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            # Requests doesn't support trailers
            # 'TE': 'trailers',
            'If-None-Match': 'W/12ca6-fJ9VuBjs5JQlhuEkVp8z810Oevs',
        }
        try:
            game_json = requests.get(url, cookies=cookies, headers=headers).json()
            game_json.raise_for_status()
        except requests.exceptions.RequestException as e:
            print("Error making api request: ", e)
        print(game_json)


        # log.info("json_request reached g2a")
        # url = "https://www.g2a.com/search/api/v2/products"
        #
        # params = {
        #     "itemsPerPage": "18",
        #     "include[0]": "filters",
        #     "currency": "EUR",
        #     "isWholesale": "false",
        #     "f[product-kind][0]": "10",
        #     "f[product-kind][1]": "8",
        #     "f[device][0]": "1118",
        #     "f[regions][0]": "8355",
        #     "category": "189",
        #     "phrase": "dead by daylight"
        # }
        #


        # async with aiohttp.ClientSession() as session:
        #     async with session.get(url, headers=headers, params=params) as response:
        #         game_json = await response.json()
        # game_json = requests.get(url, headers=header, params=params).json()
        # print(game_json)


async def setup(bot):
    await bot.add_cog(General(bot))

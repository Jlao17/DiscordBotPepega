import random
import io
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import asyncio

from helpers import checks, db_connect


class Choice(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Heads", style=discord.ButtonStyle.blurple)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "heads"
        self.stop()

    @discord.ui.button(label="Tails", style=discord.ButtonStyle.blurple)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "tails"
        self.stop()


class RockPaperScissors(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Scissors", description="You choose scissors.", emoji="✂"
            ),
            discord.SelectOption(
                label="Rock", description="You choose rock.", emoji="🪨"
            ),
            discord.SelectOption(
                label="paper", description="You choose paper.", emoji="🧻"
            ),
        ]
        super().__init__(
            placeholder="Choose...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        choices = {
            "rock": 0,
            "paper": 1,
            "scissors": 2,
        }
        user_choice = self.values[0].lower()
        user_choice_index = choices[user_choice]

        bot_choice = random.choice(list(choices.keys()))
        bot_choice_index = choices[bot_choice]

        result_embed = discord.Embed(color=0x9C84EF)
        result_embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)

        if user_choice_index == bot_choice_index:
            result_embed.description = f"**That's a draw!**\nYou've chosen {user_choice} and I've chosen {bot_choice}."
            result_embed.colour = 0xF59E42
        elif user_choice_index == 0 and bot_choice_index == 2:
            result_embed.description = f"**You won!**\nYou've chosen {user_choice} and I've chosen {bot_choice}."
            result_embed.colour = 0x9C84EF
        elif user_choice_index == 1 and bot_choice_index == 0:
            result_embed.description = f"**You won!**\nYou've chosen {user_choice} and I've chosen {bot_choice}."
            result_embed.colour = 0x9C84EF
        elif user_choice_index == 2 and bot_choice_index == 1:
            result_embed.description = f"**You won!**\nYou've chosen {user_choice} and I've chosen {bot_choice}."
            result_embed.colour = 0x9C84EF
        else:
            result_embed.description = f"**I won!**\nYou've chosen {user_choice} and I've chosen {bot_choice}."
            result_embed.colour = 0xE02B2B
        await interaction.response.edit_message(embed=result_embed, content=None, view=None)


class RockPaperScissorsView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(RockPaperScissors())


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot):
        self.bot = bot
        self.width = 10
        self.height = 10
        self.cheats = [0]  # cheats disabled by default
        self.coords = []
        self.words1 = ['monkey', 'water', 'sexy', 'mouse', 'cherry', 'computer', 'laptop', 'book']
        self.words2 = ['monkey', 'water', 'sexy', 'mouse', 'cherry', 'computer', 'laptop', 'book']

    async def reqjson(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()

    @commands.hybrid_command(
        name="randomfact",
        description="Get a random fact."
    )
    @checks.not_blacklisted()
    async def randomfact(self, context: Context) -> None:
        """
        Get a random fact.
        
        :param context: The hybrid command context.
        """
        # This will prevent your bot from stopping everything when doing a web request - see: https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-make-a-web-request
        async with aiohttp.ClientSession() as session:
            async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as request:
                if request.status == 200:
                    data = await request.json()
                    embed = discord.Embed(
                        description=data["text"],
                        color=0xD75BF4
                    )
                else:
                    embed = discord.Embed(
                        title="Error!",
                        description="There is something wrong with the API, please try again later",
                        color=0xE02B2B
                    )
                await context.send(embed=embed)

    @commands.hybrid_command(
        name="coinflip",
        description="Make a coin flip, but give your bet before."
    )
    @checks.not_blacklisted()
    async def coinflip(self, context: Context) -> None:
        """
        Make a coin flip, but give your bet before.
        
        :param context: The hybrid command context.
        """
        buttons = Choice()
        embed = discord.Embed(
            description="What is your bet?",
            color=0x9C84EF
        )
        message = await context.send(embed=embed, view=buttons)
        await buttons.wait()  # We wait for the user to click a button.
        result = random.choice(["heads", "tails"])
        print(buttons.value)
        if buttons.value == result:
            embed = discord.Embed(
                description=f"Correct! You guessed `{buttons.value}` and I flipped the coin to `{result}`.",
                color=0x9C84EF
            )
        else:
            embed = discord.Embed(
                description=f"Woops! You guessed `{buttons.value}` and I flipped the coin to `{result}`, better luck next time!",
                color=0xE02B2B
            )
        await message.edit(embed=embed, view=None, content=None)

    @commands.hybrid_command(
        name="rps",
        description="Play the rock paper scissors game against the bot."
    )
    @checks.not_blacklisted()
    async def rock_paper_scissors(self, context: Context) -> None:
        """
        Play the rock paper scissors game against the bot.
        
        :param context: The hybrid command context.
        """
        view = RockPaperScissorsView()
        await context.send("Please make your choice", view=view)

    @commands.hybrid_command()
    async def test(self, ctx, id):
        db_connect.startsql.execute("INSERT INTO blacklist (user_id) VALUES (%s)", (id,))
        await ctx.send(f"Succesful")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def yep(self, message):
        if message.channel.nsfw:
            my_files = [
                discord.File('Pictures/gt1.jpg'),
                discord.File('Pictures/gt2.jpg'),
                discord.File('Pictures/gt3.jpg'),
                discord.File('Pictures/gt4.jpg')
            ]
            await message.channel.send(files=my_files)
        else:
            e = discord.Embed(colour=discord.Colour.dark_red(),
                              description='<:error:741756417144389637> You cannot use this here!')
            await message.channel.send(embed=e)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pp(self, ctx, user=None):
        try:
            length = random.randint(0, 15)
            if length > 13:
                text = ' HOLY SHIT.'
            elif 6 <= length < 14:
                text = " nice."
            else:
                text = " so tiny."
            pp = "8" + length * "=" + "D"
            if user is None or ctx.author == ctx.message.mentions[0]:
                e = discord.Embed(colour=discord.Colour.dark_grey(), title="Peepee measurer",
                                  description="Measuring pp...")
                msg = await ctx.send(embed=e)
                await asyncio.sleep(2)
                e = discord.Embed(colour=discord.Colour.dark_grey(), title="Peepee measurer",
                                  description=f"{ctx.author.name}'s pp, {text}\n"
                                              f"{pp} `{length}` inch")
                await msg.edit(embed=e)
            else:
                e = discord.Embed(colour=discord.Colour.dark_grey(), title="Peepee measurer",
                                  description="Measuring pp...")
                msg = await ctx.send(embed=e)
                await asyncio.sleep(2)
                e = discord.Embed(colour=discord.Colour.dark_grey(), title="Peepee measurer",
                                  description=f"{ctx.message.mentions[0]}'s pp, {text}\n"
                                              f"{pp} `{length}` inch")
                await msg.edit(embed=e)

        except (AttributeError, IndexError):
            await ctx.send("I cannot find the user", delete_after=5)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pat(self, ctx, mention=None):
        e = discord.Embed(colour=discord.Colour.dark_blue())
        pat = await self.reqjson("http://api.nekos.fun:8080/api/pat")
        print(pat["image"])
        try:
            if mention is None or ctx.author == ctx.message.mentions[0]:
                e.set_author(name="{} patted himself :(".format(ctx.author))
                e.set_image(url=pat["image"])
                await ctx.send(embed=e)
            else:
                e.set_author(name=str(ctx.author) + " patted " + str(ctx.message.mentions[0]))
                e.set_image(url=pat["image"])
                await ctx.send(embed=e)
        except (AttributeError, IndexError):
            await ctx.send("I cannot find the user", delete_after=5)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def hug(self, ctx, mention=None):
        e = discord.Embed(colour=discord.Colour.dark_blue())
        hug = await self.reqjson("http://api.nekos.fun:8080/api/hug")
        print(hug["image"])
        try:
            if mention is None or ctx.author == ctx.message.mentions[0]:
                e.set_author(name="{} hugged himself :(".format(ctx.author))
                e.set_image(url=hug["image"])
                await ctx.send(embed=e)
            else:
                e.set_author(name=str(ctx.author) + " hugged " + str(ctx.message.mentions[0]))
                e.set_image(url=hug["image"])
                await ctx.send(embed=e)
        except (AttributeError, IndexError):
            await ctx.send("I cannot find the user", delete_after=5)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def horny(self, ctx, member: discord.Member = None):
        '''Horny license just for u'''
        member = member or ctx.author
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'https://some-random-api.ml/canvas/horny?avatar={member.display_avatar}'
            ) as af:
                if 300 > af.status >= 200:
                    fp = io.BytesIO(await af.read())
                    file = discord.File(fp, "horny.png")
                    em = discord.Embed(
                        title="bonk",
                        color=0xf1f1f1,
                    )
                    em.set_image(url="attachment://horny.png")
                    await ctx.send(embed=em, file=file)
                else:
                    await ctx.send('No horny :(')
                await session.close()

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lolice(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'https://some-random-api.ml/canvas/lolice?avatar={member.display_avatar}'
            ) as af:
                if 300 > af.status >= 200:
                    fp = io.BytesIO(await af.read())
                    file = discord.File(fp, "lolice.png")
                    em = discord.Embed(
                        title="Caught in 4k",
                        color=0xf1f1f1,
                    )
                    em.set_image(url="attachment://lolice.png")
                    await ctx.send(embed=em, file=file)
                else:
                    await ctx.send('No lolice :(')
                await session.close()

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def simp(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'https://some-random-api.ml/canvas/simpcard?avatar={member.display_avatar}'
            ) as af:
                if 300 > af.status >= 200:
                    fp = io.BytesIO(await af.read())
                    file = discord.File(fp, "simp.png")
                    em = discord.Embed(
                        title="Simp ;)",
                        color=0xf1f1f1,
                    )
                    em.set_image(url="attachment://simp.png")
                    await ctx.send(embed=em, file=file)
                else:
                    await ctx.send('No simp found :(')
                await session.close()

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def stupid(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'https://some-random-api.ml/canvas/its-so-stupid?avatar={member.display_avatar}?dog=test'
            ) as af:
                if 300 > af.status >= 200:
                    fp = io.BytesIO(await af.read())
                    file = discord.File(fp, "stupid.png")
                    em = discord.Embed(
                        title="It's so stupid",
                        color=0xf1f1f1,
                    )
                    em.set_image(url="attachment://stupid.png")
                    await ctx.send(embed=em, file=file)
                else:
                    await ctx.send('No stupid :(')
                await session.close()

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def insecure(self, ctx, username=None):
        insecure = random.randint(0, 100)
        if insecure > 80:
            emoji = "😳"
        elif insecure < 20:
            emoji = "😎"
        else:
            emoji = "🤔"
        try:

            if username is None:
                text = f"{ctx.author.mention} is {insecure}% insecure! {emoji}"
            else:
                text = f"{ctx.message.mentions[0]} is {insecure}% insecure! {emoji}"
            await ctx.send(text)

        except (IndexError, AttributeError):
            await ctx.send("I cannot find the user")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def depression(self, ctx, username=None):
        insecure = random.randint(0, 100)
        if insecure > 80:
            emoji = "😳"
        elif insecure < 20:
            emoji = "😎"
        else:
            emoji = "🤔"
        try:

            if username is None:
                text = f"{ctx.author.mention} is at {insecure}% depression! {emoji}"
            else:
                text = f"{ctx.message.mentions[0]} is at {insecure}% depression! {emoji}"
            await ctx.send(text)

        except (IndexError, AttributeError):
            await ctx.send("I cannot find the user")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tictactoe(self, ctx, mentions=None):
        gameid = '`' + str(random.randint(1000, 9999)) + '`'
        winplayer1 = []
        winplayer2 = []
        nummers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

        if mentions is None:
            await ctx.send("You need to ping the user to play tic tac toe with each other")
            return
        else:
            await ctx.send("I need confirmation of the pinged user, respond with `yes` to confirm.")
            flag = True
            while flag:
                try:
                    msg = await self.bot.wait_for('message',
                                                  check=lambda message: message.author.id == ctx.message.mentions[0].id,
                                                  timeout=10)
                except asyncio.TimeoutError:
                    await ctx.send("Pinged user didn't respond...")
                    return
                if msg.content.lower() == "yes" and msg.channel == ctx.channel:
                    await ctx.send("<a:yes:776600445702897704> | Confirmation received, game starting ...")
                    flag = False

        def checkwin(lijst):
            #win conditions
            win1 = [1, 2, 3]
            win2 = [1, 4, 7]
            win3 = [3, 6, 9]
            win4 = [7, 8, 9]
            win5 = [1, 5, 9]
            win6 = [3, 5, 7]
            win7 = [4, 5, 6]
            win8 = [2, 5, 8]
            if all(x in lijst for x in win1):
                return 0, win1
            elif all(x in lijst for x in win2):
                return 0, win2
            elif all(x in lijst for x in win3):
                return 0, win3
            elif all(x in lijst for x in win4):
                return 0, win4
            elif all(x in lijst for x in win5):
                return 0, win5
            elif all(x in lijst for x in win6):
                return 0, win6
            elif all(x in lijst for x in win7):
                return 0, win7
            elif all(x in lijst for x in win8):
                return 0, win8
            else:
                return 1, []

        def kanker(pos, player):
            if player == 1:
                nummers[pos] = 'X'
            elif player == 2:
                nummers[pos] = 'O'
            elif player == 'X' or player == 'O':
                nummers[pos[0]] = "**" + str(player) + "**"
                nummers[pos[1]] = "**" + str(player) + "**"
                nummers[pos[2]] = "**" + str(player) + "**"

            format = nummers[1] + '|' + nummers[2] + '|' + nummers[3] + '\n' + '-----\n' + nummers[4] + '|' + \
                     nummers[5] + '|' + nummers[6] + '\n' + '-----\n' + nummers[7] + '|' + nummers[8] + '|' + nummers[9]

            return format

        await ctx.send(
            'Player 1 starts: ' + str(ctx.author.mention) + '| Game ID:' + gameid + '| `q`or`quit` to quit' +
            '\n1' + '|' + '2' + '|' + '3' + '\n' + '-----\n' + '4' + '|' + '5' + '|' + '6' + '\n' + '-----\n' +
            '7' + '|' + '8' + '|' + '9')
        flagmain = True
        while flagmain:
            flag = True
            while flag:
                try:
                    player1 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                                      timeout=15)
                except asyncio.TimeoutError:
                    await ctx.send("Time's up, user didn't respond")
                    await ctx.send("Game {} ended by the user".format(gameid))
                    return
                try:
                    if player1.content == 'q' or player1.content == 'quit':
                        await ctx.send("")
                        return
                    elif 0 < int(player1.content) < 10 and int(player1.content) not in winplayer1 and int(player1.content) not in winplayer2:
                        winplayer1.append(int(player1.content))
                        if checkwin(winplayer1)[0] == 0:
                            kanker(int(player1.content), 1)
                            kanker(checkwin(winplayer1)[1], 'X')
                            await ctx.send(kanker(0, 0))
                            await ctx.send("{} won!".format(ctx.author.mention))
                            return
                        elif len(winplayer1) + len(winplayer2) == 9:
                            await ctx.send("Tie, game {} ended".format(gameid))
                            return
                        else:
                            print(winplayer1)
                            await ctx.send('Player 2 is: ' + str(ctx.message.mentions[0].mention) + '| Game ID:' +
                                           gameid + '| `q`or`quit` to quit' + '\n' + kanker(int(player1.content), 1))
                            flag = False
                    else:
                        await ctx.send("You cannot do that, try again or type `q`/`quit` to quit")
                except ValueError:
                    await ctx.send("Woa chill, that's not possible, try again")
            flag = True
            while flag:
                try:
                    player1 = await self.bot.wait_for('message', check=lambda message:
                    message.author.id == ctx.message.mentions[0].id, timeout=15)
                except asyncio.TimeoutError:
                    await ctx.send("Time's up, user didn't respond")
                    return
                try:
                    if player1.content == 'q' or player1.content == 'quit':
                        await ctx.send("Game {} ended by the user".format(gameid))
                        return
                    elif 0 < int(player1.content) < 10 and int(player1.content) not in winplayer2 and int(player1.content) not in winplayer1:
                        winplayer2.append(int(player1.content))
                        if checkwin(winplayer2)[0] == 0:
                            kanker(int(player1.content), 2)
                            kanker(checkwin(winplayer2)[1], 'O')
                            await ctx.send(kanker(0, 0))
                            await ctx.send("{} won!".format(ctx.message.mentions[0].mention))
                            return
                        else:
                            print(winplayer2)
                            await ctx.send('Player 1 is: ' + str(ctx.author.mention) + '| Game ID:' + gameid +
                                           '| `q` or`quit` to quit' + '\n' + kanker(int(player1.content), 2))
                            flag = False
                    else:
                        await ctx.send("You cannot do that, try again or type q/quit to quit")
                except ValueError:
                    await ctx.send("Woa chill, that's not possible, try again")

        await ctx.send("Game {} ended".format(gameid))


async def setup(bot):
    await bot.add_cog(Fun(bot))

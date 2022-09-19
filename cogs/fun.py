import random

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context
import asyncio
import string

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

    @commands.hybrid_command()
    async def woordzoeker(self, ctx):
        await ctx.send("Hello. Welcome to Word Search\u2122")
        choicegrid = await self.choicegrid(ctx)
        if choicegrid == 1:
            return
        choicewords = await self.choicewords(ctx)
        if choicewords == 1:
            return

        self.words1 = [x.upper() for x in self.words1]
        grid = [[format('. ') for i in range(0, self.width)] for j in range(0, self.height)]
        for word in self.words1:
            grid = await self.wordingrid(word, grid)
        grid = [[x.replace('. ', (random.choice(string.ascii_uppercase) + ' ')) for x in l] for l in grid]
        woordenlijst = await self.printwords()
        #  Adding the numbers on output screen for better readability
        firstpart = ''
        for k in range(self.height + 1):
            if k > 0:
                if k > 10:
                    firstpart += (' ' + str(k))
                else:
                    firstpart += (' ' + str(k))
            else:
                firstpart += (' ' + str(k))
        firstpart += f" Type q to quit the game | Word list: {woordenlijst}"

        secondpart = ''
        for c, value in enumerate(grid, 1):
            if c < 10:
                txt = (' ' + str(c) + ' ' + '\n'.join('').join(value) + '\n')
                secondpart += txt
            else:
                txt = (str(c) + ' ' + '\n'.join('').join(value) + '\n')
                secondpart += txt
        await ctx.send(f"```\n"
                       f"{firstpart}\n"
                       f"{secondpart}"
                       f"```")
        # shows the coords for every word in the grid (disabled by default)
        if self.cheats[0] == 1:
            await ctx.send(f"Cheats: {self.coords}")

        flag = True
        while flag:
            if self.words2:  # check if list is not empty
                try:
                    woord = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author,
                                                    timeout=60)
                except asyncio.TimeoutError:
                    await ctx.send("Time's up, user didn't respond, gg")
                    return
                if woord == 'q':
                    await ctx.send("Exiting game...")
                    self.coords = []
                    flag = False
                # Checks if the input coords are in the list 'coords'.
                elif woord in (x[0] for x in self.coords):
                    for l in self.coords:
                        if l[0] == woord:
                            if l[1] in self.words2:
                                print("You've found the word!")
                                self.words2.remove(l[1])
                                self.words1.remove(l[1].upper())
                    if self.words2:
                        await self.printwords()
                else:
                    print("Wrong")
            else:
                print("congratulations, you've found all words!")
                print("-------------------------------------------")
                print("You are now back in the Word Search menu. What would you like to do?")
                self.coords = []
                flag = False

    async def wordingrid(self, word, grid):
        flag = True
        counterphase2 = 0
        while flag:
            counterphase1 = 0
            # Get to know when the word is flipped or not for future references
            choice = random.randint(0, 1)
            if choice == 0:
                pass
            else:
                word = word[::-1]

            d = random.choice([[1, 0], [0, 1], [1, 1]])  # Positions for each word possible in steps
            xsize = self.width if d[0] == 0 else self.width - len(word)
            ysize = self.height if d[1] == 0 else self.height - len(word)
            while counterphase1 < 10:
                x = random.randrange(0, xsize)
                y = random.randrange(0, ysize)
                for i in range(0, len(word)):  # checks if word fits in the grid
                    if grid[y + d[1] * i][x + d[0] * i] not in ['. ', word[i]]:
                        counterphase1 += 1  # counter to allow 10 tries before going to the next phase
                        break
                else:
                    counterphase1 = 20
                    break

            # next phase: it will try the whole code again with another choice in line 15
            if counterphase1 == 10:
                counterphase2 += 1
                # counter to allow 10 tries in while loop before it gives up placing the word in the grid.
                if counterphase2 == 10:
                    flag = False
            else:
                count = -1
                word2 = ''
                # Get to know the element in self.words1 and use that in self.words2
                for k in self.words1:
                    count += 1
                    if choice == 0:
                        if k.upper() == word:
                            word2 = self.words2[count]
                    else:
                        if k.upper() == word[::-1]:
                            word2 = self.words2[count]
                for i in range(0, len(word)):  # puts the word in the grid
                    grid[y + d[1] * i][x + d[0] * i] = (word[i] + " ")
                # Puts the coords and the displayed word in list for future references
                if choice == 0:
                    self.coords.append([str(x + 1) + str(y + 1), word2])
                else:
                    word = word[::-1]
                    self.coords.append([str(x + d[0] * i + 1) + str(y + d[1] * i + 1), word2])
                flag = False
        return grid

    async def printwords(self):
        print("Words left to find:", end=" ")
        woordenlijst = ''
        for woorden in self.words2:
            woordenlijst += (woorden + " ")
        return woordenlijst

    async def makelist(self, option):
        while option < len(self.words2):
            randnumber = random.randint(0, (len(self.words2) - 1))
            del self.words1[randnumber]
            del self.words2[randnumber]

    async def choicegrid(self, ctx):
        flag = True
        while flag:
            await ctx.send("What is your custom grid? (10-20)")
            try:
                msg = await self.bot.wait_for('message',
                                              check=lambda message: message.author.id == ctx.author.id,
                                              timeout=10)
            except asyncio.TimeoutError:
                await ctx.send("User didn't respond...")
                return 1
            try:
                choicegrid = int(msg.content)
                await ctx.send("DONE, GRID IS {}".format(choicegrid))
                return choicegrid
            except ValueError:
                await ctx.send("Not a number, try again...")

    async def choicewords(self, ctx):
        flag2 = True
        while flag2:
            await ctx.send("How many words do you want to find?\nNOTE: maximum words of your custom grid minus 2 "
                           "(" + str(self.width - 2) + ").")
            try:
                msg = await self.bot.wait_for('message',
                                              check=lambda message: message.author.id == ctx.author.id,
                                              timeout=10)
            except asyncio.TimeoutError:
                await ctx.send("User didn't respond...")
                return 1
            try:
                choicewords = int(msg.content)
                if int(choicewords) < 1:
                    await ctx.send("It can't be lower than 1, try again...")
                elif int(choicewords) > (self.width - 2):
                    await ctx.send("It can't be higher than the maximum words, try again...")
                else:
                    return choicewords
            except ValueError:
                await ctx.send("Not a number, try again...")


async def setup(bot):
    await bot.add_cog(Fun(bot))

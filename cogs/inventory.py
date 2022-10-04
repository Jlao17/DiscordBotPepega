import math

import discord
from discord.ext import commands
from helpers import db_connect
from operator import itemgetter
from discord.ui import Button, View
from helpers import checks


class Inventory(commands.Cog, name="inventory"):
    def __init__(self, bot):
        self.bot = bot
        self.sql = db_connect.startsql
        self.helpGuide = []
        self.button_next = False
        self.button_back = True
        self.startstoredfields = {0: 0, 1: 5, 2: 10, 3: 15, 4: 20, 5: 25}
        self.storedfields = []

    def createHelpEmbed(self, title, pageNum=0, inline=False):
        print(1)
        embed = discord.Embed(colour=discord.Colour.blurple(), title=title)
        # print(self.storedfields, pageNum)
        # print(self.storedfields[self.startstoredfields[pageNum]:(self.startstoredfields[pageNum+1]-1)], self.startstoredfields[pageNum], self.startstoredfields[pageNum+1]-1)
        for field in self.storedfields[self.startstoredfields[pageNum]:self.startstoredfields[pageNum + 1]]:
            print(field[0], field[1], field[2], field[3])
            embed.add_field(name=f"{field[0]} {field[1]} ― {field[2]}", value=field[3], inline=inline)
        embed.set_footer(text=f"Page {pageNum + 1} of {math.ceil(len(self.storedfields) / 5)}")
        # print(self.startstoredfields[pageNum + 1], len(self.storedfields), self.startstoredfields[pageNum+2])

        # Check whether button should be disabled or not
        print(self.startstoredfields[pageNum + 1], len(self.storedfields), self.startstoredfields[pageNum + 2])
        if self.startstoredfields[pageNum + 1] < len(self.storedfields) < self.startstoredfields[pageNum + 2]:
            self.button_next = False
            print("button_next disabled")
        else:
            self.button_next = True
            print("button_next enabled")
        if self.startstoredfields[pageNum + 1] > len(self.storedfields):
            self.button_back = False
            print("button_back enabled")
        else:
            self.button_back = True
            print("button_back disabled")

        return embed

    @commands.hybrid_command(
        name="inventory",
        description="Open your inventory.",
    )
    async def inventory(self, ctx, discordid=None):
        self.storedfields = []
        currentPage = 0
        nextButton = Button(label=">", style=discord.ButtonStyle.blurple)
        backButton = Button(label="<", style=discord.ButtonStyle.blurple, disabled=True)

        myview = View(timeout=180)
        myview.add_item(backButton)
        myview.add_item(nextButton)

        async def next_callback(interaction):
            nonlocal currentPage
            currentPage += 1
            await buttons_function(interaction)

        async def back_callback(interaction):
            nonlocal currentPage
            currentPage -= 1
            await buttons_function(interaction)

        async def buttons_function(interaction):
            embed = self.createHelpEmbed("Inventory", pageNum=currentPage)
            if not self.button_next:
                if self.button_back:
                    backButton.disabled = True
                else:
                    backButton.disabled = False
                nextButton.disabled = False
                await interaction.response.edit_message(embed=embed, view=myview)
            else:
                if self.button_back:
                    backButton.disabled = True
                else:
                    backButton.disabled = False
                nextButton.disabled = True
                await interaction.response.edit_message(embed=embed, view=myview)

        nextButton.callback = next_callback
        backButton.callback = back_callback
        # ---------------------------------------------------- button shit testing

        if discordid is None:
            discordid = ctx.message.author.id
        # record = self.sql.fetchone("SELECT * FROM user WHERE userid = (%s)", (discordid,))
        userinventory = self.sql.fetchall("SELECT * FROM inventory WHERE userid = (%s)", (discordid,))
        e = discord.Embed(colour=discord.Colour.dark_blue())
        e.set_author(name="Inventory")
        for useritem in userinventory:
            items = self.sql.fetchall("SELECT * FROM item WHERE itemid = (%s)", (useritem[1],))
            for iteminfo in items:
                self.storedfields.append([iteminfo[3], iteminfo[1], useritem[2], iteminfo[2]])
                # iteminfo[3] is icon, iteminfo[1] is item name, useritem[2] is amount, iteminfo[2] is item description
                # e.add_field(name=f"{iteminfo[3]} {iteminfo[1]} ― {str(useritem[2])}", value=iteminfo[2], inline=False)
        # sorteer op basis van naam - index 1
        self.storedfields = sorted(self.storedfields, key=itemgetter(1))
        # for field in storedfields:
        #    e.add_field(name=f"{field[0]} {field[1]} ― {field[2]}", value=field[3], inline=False)
        if len(self.storedfields) < self.startstoredfields[currentPage + 1]:
            print("disabled")
            nextButton.disabled = True
        print(len(self.storedfields), self.startstoredfields[currentPage + 1])
        await ctx.send(embed=self.createHelpEmbed(title="Inventory", pageNum=0), view=myview)


async def setup(bot):
    await bot.add_cog(Inventory(bot))

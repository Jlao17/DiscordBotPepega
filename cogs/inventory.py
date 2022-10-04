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
        self.start_stored_fields = {0: 0, 1: 5, 2: 10, 3: 15, 4: 20, 5: 25}
        self.stored_fields = []

    def create_help_embed(self, title, page_num=0, inline=False):
        print(1)
        embed = discord.Embed(colour=discord.Colour.blurple(), title=title)
        # print(self.stored_fields, pageNum) print(self.stored_fields[self.start_stored_fields[page_num]:(
        # self.start_stored_fields[page_num+1]-1)], self.start_stored_fields[page_num], self.start_stored_fields[
        # page_num+1]-1)
        for field in self.stored_fields[self.start_stored_fields[page_num]:self.start_stored_fields[page_num + 1]]:
            print(field[0], field[1], field[2], field[3])
            embed.add_field(name=f"{field[0]} {field[1]} ― {field[2]}", value=field[3], inline=inline)
        embed.set_footer(text=f"Page {page_num + 1} of {math.ceil(len(self.stored_fields) / 5)}")
        # print(self.start_stored_fields[page_num + 1], len(self.stored_fields), self.start_stored_fields[page_num+2])

        # Check whether button should be disabled or not
        print(self.start_stored_fields[page_num + 1], len(self.stored_fields), self.start_stored_fields[page_num + 2])
        if self.start_stored_fields[page_num + 1] < len(self.stored_fields) < self.start_stored_fields[page_num + 2]:
            self.button_next = False
            print("button_next disabled")
        else:
            self.button_next = True
            print("button_next enabled")
        if self.start_stored_fields[page_num + 1] > len(self.stored_fields):
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
    async def inventory(self, ctx, discord_id=None):
        self.stored_fields = []
        current_page = 0
        next_button = Button(label=">", style=discord.ButtonStyle.blurple)
        back_button = Button(label="<", style=discord.ButtonStyle.blurple, disabled=True)

        my_view = View(timeout=180)

        my_view.add_item(back_button)
        my_view.add_item(next_button)

        async def next_callback(interaction):
            nonlocal current_page
            current_page += 1
            await buttons_function(interaction)

        async def back_callback(interaction):
            nonlocal current_page
            current_page -= 1
            await buttons_function(interaction)

        async def buttons_function(interaction):
            embed = self.create_help_embed("Inventory", page_num=current_page)
            if not self.button_next:
                if self.button_back:
                    back_button.disabled = True
                else:
                    back_button.disabled = False
                next_button.disabled = False
                await interaction.response.edit_message(embed=embed, view=my_view)
            else:
                if self.button_back:
                    back_button.disabled = True
                else:
                    back_button.disabled = False
                next_button.disabled = True
                await interaction.response.edit_message(embed=embed, view=my_view)

        next_button.callback = next_callback
        back_button.callback = back_callback
        # ---------------------------------------------------- button shit testing

        if discord_id is None:
            discord_id = ctx.message.author.id
        # record = self.sql.fetchone("SELECT * FROM user WHERE userid = (%s)", (discordid,))
        user_inventory = self.sql.fetchall("SELECT * FROM inventory WHERE userid = (%s)", (discord_id,))
        e = discord.Embed(colour=discord.Colour.dark_blue())
        e.set_author(name="Inventory")
        for user_item in user_inventory:
            items = self.sql.fetchall("SELECT * FROM item WHERE itemid = (%s)", (user_item[1],))
            for item_info in items:
                self.stored_fields.append([item_info[3], item_info[1], user_item[2], item_info[2]])
                # item_info[3] is icon, item_info[1] is item name, user_item[2] is amount, item_info[2] is item
                # description e.add_field(name=f"{item_info[3]} {item_info[1]} ― {str(user_item[2])}",
                # value=item_info[2], inline=False) 
        # sorteer op basis van naam - index 1
        self.stored_fields = sorted(self.stored_fields, key=itemgetter(1))
        # for field in stored_fields:
        #    e.add_field(name=f"{field[0]} {field[1]} ― {field[2]}", value=field[3], inline=False)
        if len(self.stored_fields) < self.start_stored_fields[current_page + 1]:
            print("disabled")
            next_button.disabled = True
        print(len(self.stored_fields), self.start_stored_fields[current_page + 1])
        await ctx.send(embed=self.create_help_mbed(title="Inventory", page_num=0), view=my_view)


async def setup(bot):
    await bot.add_cog(Inventory(bot))

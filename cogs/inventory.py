import discord
from discord.ext import commands
from helpers import db_connect
from operator import itemgetter
from helpers import checks


# Here we name the cog and create a new class for the cog.
class Inventory(commands.Cog, name="inventory"):
    def __init__(self, bot):
        self.bot = bot
        self.sql = db_connect.startsql

    @commands.hybrid_command(
        name="inventory",
        description="Open your inventory.",
    )
    async def inventory(self, ctx, discordid=None):
        storedfields = []
        if discordid is None:
            discordid = ctx.message.author.id
        # record = self.sql.fetchone("SELECT * FROM user WHERE userid = (%s)", (discordid,))
        userinventory = self.sql.fetchall("SELECT * FROM inventory WHERE userid = (%s)", (discordid,))
        e = discord.Embed(colour=discord.Colour.dark_blue())
        e.set_author(name="Inventory")
        for useritem in userinventory:
            items = self.sql.fetchall("SELECT * FROM item WHERE itemid = (%s)", (useritem[1],))
            for iteminfo in items:
                storedfields.append([iteminfo[3], iteminfo[1], useritem[2], iteminfo[2]])
                # iteminfo[3] is icon, iteminfo[1] is item name, useritem[2] is amount, iteminfo[2] is item description
                # e.add_field(name=f"{iteminfo[3]} {iteminfo[1]} ― {str(useritem[2])}", value=iteminfo[2], inline=False)
        # sorteer op basis van naam - index 1
        storedfields = sorted(storedfields, key=itemgetter(1))
        for field in storedfields:
            e.add_field(name=f"{field[0]} {field[1]} ― {field[2]}", value=field[3], inline=False)
        await ctx.send(embed=e)


async def setup(bot):
    await bot.add_cog(Inventory(bot))

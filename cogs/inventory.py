import discord
from discord.ext import commands
from helpers import db_connect
from helpers import checks


# Here we name the cog and create a new class for the cog.
class Inventory(commands.Cog, name="inventory"):
    def __init__(self, bot):
        self.bot = bot
        self.sql = db_connect.startsql


    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.
    @commands.hybrid_command(
        name="inventory",
        description="Open your inventory.",
    )
    async def inventory(self, ctx, discordid=None):
        if discordid is None:
            discordid = ctx.message.author.id
        # record = self.sql.fetchone("SELECT * FROM user WHERE userid = (%s)", (discordid,))
        userinventory = self.sql.fetchall("SELECT * FROM inventory WHERE userid = (%s)", (discordid,))
        e = discord.Embed(colour=discord.Colour.dark_blue())
        e.set_author(name="Inventory")
        for item in userinventory:
            items = self.sql.fetchall("SELECT * FROM item WHERE itemid = (%s)", (item[1],))
            for iteminfo in items:
                e.add_field(name=(iteminfo[1] + " ― " + str(item[2])), value=iteminfo[2], inline=False)

        await ctx.send(embed=e)



# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot):
    await bot.add_cog(Inventory(bot))
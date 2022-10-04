import copy

from discord.ext import commands
from helpers import db_connect
import random

from helpers import checks


# Here we name the cog and create a new class for the cog.
class Open(commands.Cog, name="open"):
    def __init__(self, bot):
        self.bot = bot
        self.sql = db_connect.startsql
        self.normal_box = [[0, 100, "legendary"], [100, 7100, "common"], [7100, 9100, "uncommon"],
                           [9100, 10001, "rare"]]
        self.rare_box = [[0, 500, "legendary"], [500, 7100, "common"], [7100, 8500, "uncommon"],
                         [8500, 10001, "rare"]]

    @commands.hybrid_command(
        name="open",
        description="Open a lootbox in your inventory.",
    )
    # This will only allow non-blacklisted members to execute the command
    async def open(self, ctx, arg=None):
        if arg is None:
            await ctx.send("Please provide an item!")
            return
        elif arg.lower() == "common":
            rates_copy = copy.deepcopy(self.normal_box)
        elif arg.lower() == "rare":
            rates_copy = copy.deepcopy(self.rare_box)
        else:
            await ctx.send("Provided argument does not exist.")
            return

        rng = random.randint(0, 10000)
        modifier = self.sql.fetchone("SELECT modifier FROM user WHERE userid = (%s)", (ctx.message.author.id,))[0]
        rates_copy[0][1] += modifier
        rates_copy[1][0] += modifier
        for rates in rates_copy:
            if rates[0] < rng < rates[1]:
                await ctx.send(f"You found a {rates[2]}.")
                return


async def setup(bot):
    await bot.add_cog(Open(bot))

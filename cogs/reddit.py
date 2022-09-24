import praw
from discord.ext import commands, tasks
import discord
import json
from helpers import db_connect


class Reddit(commands.Cog, name="reddit"):

    def __init__(self, bot):
        self.client = ""
        self.secret = ""
        self.agent = ""
        self.bot = bot
        self.updatepost.start()
        self.getkey()
        self.sql = db_connect.startsql

    def getkey(self):
        with open('config.json') as json_file:
            data = json.load(json_file)
        self.client = data["client-id"]
        self.secret = data["secret"]
        self.agent = data["agent"]

    @tasks.loop(minutes=1440)
    async def updatepost(self):
        print("*******__Updating database Reddit__*******")

        "---------------CONNECTION REDDIT-------------------"
        reddit = praw.Reddit(client_id=self.client,
                             client_secret=self.secret,
                             user_agent=self.agent)
        "---------------------------------------------------"

        await self.sql.execute("""truncate table Meme """)
        memes_submissions = reddit.subreddit('meme').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied)
                if submission.url.endswith("jpg") or submission.url.endswith("png"):
                    await self.sql.execute("INSERT INTO Meme (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass

        memes_submissions = reddit.subreddit('dankmemes').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied)
                if submission.url.endswith("jpg") or submission.url.endswith("png") or "gif" in submission.url:
                    await self.sql.execute("INSERT INTO Meme (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass

        print("done inserting: meme")

        await self.sql.execute("""truncate table Hentai """)
        memes_submissions = reddit.subreddit('hentai').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied)
                if submission.url.endswith("jpg") or submission.url.endswith("png") or submission.url.endswith("gif") or submission.url.startswith("https://www.redgifs.com"):
                    await self.sql.execute("INSERT INTO Hentai (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass
        memes_submissions = reddit.subreddit('HENTAI_GIF').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied)
                if submission.url.endswith("gif") or submission.url.endswith("png") or submission.url.endswith("jpg") or submission.url.startswith("https://www.redgifs.com"):
                    await self.sql.execute("INSERT INTO Hentai (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass

        print("done inserting: hentai")

        await self.sql.execute("""truncate table Porn """)
        memes_submissions = reddit.subreddit('nsfw').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied)
                if submission.url.endswith("gif") or submission.url.endswith("png") or submission.url.endswith("jpg") or submission.url.startswith("https://www.redgifs.com"):
                    await self.sql.execute("INSERT INTO Porn (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass

        print("done inserting: porn")

        await self.sql.execute("""truncate table Anime """)
        memes_submissions = reddit.subreddit('cutelittlefangs').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied and not x.over_18)
                if submission.url.endswith("jpg") or submission.url.endswith("png"):
                    await self.sql.execute("INSERT INTO Anime (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass

        print("done inserting: cutelittlefangs")

        memes_submissions = reddit.subreddit('awwnime').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied and not x.over_18)
                if submission.url.endswith("jpg") or submission.url.endswith("png"):
                    await self.sql.execute("INSERT INTO Anime (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass
        print("done inserting: awwnime")

        await self.sql.execute("""truncate table Gachi """)
        memes_submissions = reddit.subreddit('gachimuchi').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied and not x.over_18)
                if submission.url.startswith("https://v.redd") or submission.url.startswith('https://www.reddit.com/r/'):
                    pass
                else:
                    await self.sql.execute("INSERT INTO Gachi (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass
        print("done inserting: gachimuchi")

        await self.sql.execute("""truncate table Food """)
        memes_submissions = reddit.subreddit('FoodPorn').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied)
                if submission.url.endswith("jpg") or submission.url.endswith("png"):
                    await self.sql.execute("INSERT INTO Food (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass
        memes_submissions = reddit.subreddit('food').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied)
                if submission.url.endswith("jpg") or submission.url.endswith("png"):
                    await self.sql.execute("INSERT INTO Food (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass
        print("done inserting: foodporn")

        print("DONE UPDATING REDDIT")

    @commands.command()
    @commands.is_owner()
    async def updatedb(self, ctx):
        await ctx.send("*******__Updating database Reddit__*******")

        "---------------CONNECTION REDDIT-------------------"
        reddit = praw.Reddit(client_id=self.client,
                             client_secret=self.secret,
                             user_agent=self.agent)
        "---------------------------------------------------"

        await self.sql.execute("""truncate table Meme """)
        memes_submissions = reddit.subreddit('meme').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied)
                if submission.url.endswith("jpg") or submission.url.endswith("png"):
                    await self.sql.execute("INSERT INTO Meme (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass

        memes_submissions = reddit.subreddit('dankmemes').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied)
                if submission.url.endswith("jpg") or submission.url.endswith("png") or "gif" in submission.url:
                    await self.sql.execute("INSERT INTO Meme (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass

        await ctx.send("done inserting: meme")

        await self.sql.execute("""truncate table Hentai """)
        memes_submissions = reddit.subreddit('hentai').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied)
                if submission.url.endswith("jpg") or submission.url.endswith("png"):
                    await self.sql.execute("INSERT INTO Hentai (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass
        memes_submissions = reddit.subreddit('HENTAI_GIF').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied)
                if submission.url.endswith("gif") or submission.url.endswith("png") or submission.url.endswith("jpg") or submission.url.startswith("https://www.redgifs.com"):
                    await self.sql.execute("INSERT INTO Hentai (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass

        await ctx.send("done inserting: hen tie")

        await self.sql.execute("""truncate table Porn """)
        memes_submissions = reddit.subreddit('nsfw').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied)
                if submission.url.endswith("gif") or submission.url.endswith("png") or submission.url.endswith("jpg") or submission.url.startswith("https://www.redgifs.com"):
                    await self.sql.execute("INSERT INTO Porn (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass
        await ctx.send("done inserting: pawn")

        await self.sql.execute("""truncate table Anime """)
        memes_submissions = reddit.subreddit('cutelittlefangs').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied and not x.over_18)
                if submission.url.endswith("jpg") or submission.url.endswith("png"):
                    await self.sql.execute("INSERT INTO Anime (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass

        await ctx.send("done inserting: cutelittlefangs")

        memes_submissions = reddit.subreddit('awwnime').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied and not x.over_18)
                if submission.url.endswith("jpg") or submission.url.endswith("png"):
                    await self.sql.execute("INSERT INTO Anime (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass
        await ctx.send("done inserting: awwnime")

        await self.sql.execute("""truncate table Gachi """)
        memes_submissions = reddit.subreddit('gachimuchi').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied and not x.over_18)
                if submission.url.startswith("https://v.redd") or submission.url.startswith('https://www.reddit.com/r/'):
                    pass
                else:
                    await self.sql.execute("INSERT INTO Gachi (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass
        await ctx.send("done inserting: gachimuchi")

        await self.sql.execute("""truncate table Food """)
        memes_submissions = reddit.subreddit('FoodPorn').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied)
                if submission.url.endswith("jpg") or submission.url.endswith("png"):
                    await self.sql.execute("INSERT INTO Food (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass
        memes_submissions = reddit.subreddit('food').hot()
        for i in range(100):
            try:
                submission = next(x for x in memes_submissions if not x.stickied)
                if submission.url.endswith("jpg") or submission.url.endswith("png"):
                    await self.sql.execute("INSERT INTO Food (title, url) VALUES (%s, %s)", (submission.title, submission.url))
            except StopIteration:
                pass
        await ctx.send("done inserting: food")

        await ctx.send("<a:yes:776600445702897704> DONE UPDATING REDDIT")

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.role)
    async def meme(self, ctx):
        e = discord.Embed(colour=discord.Colour.dark_blue())
        e.set_footer(text="requested by {}".format(ctx.author.display_name), icon_url=ctx.author.avatar_url)
        record = await self.sql.fetchone("select * from Meme ORDER BY RAND()")
        print(record)
        e.set_author(name=record[0])
        e.set_image(url=record[1])
        await ctx.send(embed=e)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.role)
    async def anime(self, ctx):
        e = discord.Embed(colour=discord.Colour.dark_blue())
        e.set_footer(text="requested by {}".format(ctx.author.display_name), icon_url=ctx.author.avatar_url)
        record = await self.sql.fetchone("select * from Anime ORDER BY RAND()")
        print(record)
        e.set_author(name=record[0])
        e.set_image(url=record[1])
        await ctx.send(embed=e)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.role)
    async def gachi(self, ctx):
        e = discord.Embed(colour=discord.Colour.dark_blue())
        e.set_footer(text="requested by {}".format(ctx.author.display_name), icon_url=ctx.author.avatar_url)
        record = await self.sql.fetchone("select * from Gachi ORDER BY RAND()")
        print(record)
        if record[1].endswith("jpg") or record[1].endswith("png"):
            e.set_author(name=record[0])
            e.set_image(url=record[1])
            await ctx.send(embed=e)
        else:
            e.set_author(name=record[0])
            await ctx.send(embed=e)
            await ctx.send(record[1])

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.role)
    async def food(self, ctx):
        e = discord.Embed(colour=discord.Colour.dark_blue())
        e.set_footer(text="requested by {}".format(ctx.author.display_name), icon_url=ctx.author.avatar_url)
        record = await self.sql.fetchone("select * from Food ORDER BY RAND()")
        print(record)
        e.set_author(name=record[0])
        e.set_image(url=record[1])
        await ctx.send(embed=e)

    # NSFW ------------------------------------------------------------------------------------------------------------

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.role)
    async def hentai(self, message):
        if message.channel.nsfw:
            e = discord.Embed(colour=discord.Colour.dark_blue())
            e.set_footer(text="requested by {}".format(message.author.display_name), icon_url=message.author.avatar_url)
            record = await self.sql.fetchone("select * from Hentai ORDER BY RAND()")
            print(record)
            e.set_author(name=record[0])
            e.set_image(url=record[1])
            await message.channel.send(embed=e)
        else:
            e = discord.Embed(colour=discord.Colour.dark_red(),
                              description='<:error:741756417144389637> You cannot use this here!')
            await message.channel.send(embed=e)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.role)
    async def porn(self, message):
        if message.channel.nsfw:
            e = discord.Embed(colour=discord.Colour.dark_blue())
            e.set_footer(text="requested by {}".format(message.author.display_name), icon_url=message.author.avatar_url)
            record = await self.sql.fetchone("select * from Porn ORDER BY RAND()")
            print(record)
            e.set_author(name=record[0])
            e.set_image(url=record[1])
            await message.channel.send(embed=e)
        else:
            e = discord.Embed(colour=discord.Colour.dark_red(),
                              description='<:error:741756417144389637> You cannot use this here!')
            await message.channel.send(embed=e)


async def setup(bot):
    await bot.add_cog(Reddit(bot))


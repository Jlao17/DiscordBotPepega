import aiomysql
import asyncio
import json
import nest_asyncio

class SQLstartup():

    def __init__(self):
        self.hostname = ""
        self.username = ""
        self.password = ""
        self.database = ""
        self.getkey()

    def getkey(self):
        with open('config.json') as json_file:
            data = json.load(json_file)
        self.hostname = data["hostname"]
        self.username = data["user"]
        self.password = data["password"]
        self.database = data["database"]

    async def pool(self, loop):
        return await aiomysql.create_pool(host=self.hostname,
                                          user=self.username,
                                          password=self.password,
                                          db=self.database,
                                          autocommit=True,
                                          loop=loop
                                          )

    async def helper(self, loop):
        self.pool = await self.pool(loop)

    async def execute(self, query, tuple=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, tuple)
                return await cur.fetchall()

    async def fetchone(self, query, tuple=None):
        print("1", query, tuple)
        async with self.pool.acquire() as conn:
            print("2")
            async with conn.cursor() as cur:
                print("3")
                await cur.execute(query, tuple)
                print("4")
                return await cur.fetchone()

    async def fetchall(self, query, tuple=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, tuple)
                return await cur.fetchall()

print("Wtf")
startsql = SQLstartup()
print("Wtf1")
loop = asyncio.get_event_loop()
print("Wtf2")
nest_asyncio.apply()
loop.run_until_complete(SQLstartup.helper(startsql, loop))
print("Wtf3")

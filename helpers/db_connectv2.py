import aiomysql
import asyncio
import json


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
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, tuple)
                return await cur.fetchone()

    async def fetchall(self, query, tuple=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, tuple)
                return await cur.fetchall()






startsql = SQLstartup()
loop = asyncio.get_event_loop()
loop.run_until_complete(SQLstartup.helper(startsql, loop))


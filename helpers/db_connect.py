import mysql.connector
from mysql.connector import Error
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

    def execute(self, query, tuple=None):
        connection = mysql.connector.connect(host=self.hostname,
                                             database=self.database,
                                             user=self.username,
                                             password=self.password)
        cur = connection.cursor(buffered=True)
        cur.execute(query, tuple)
        connection.commit()
        record = cur.fetchall()
        cur.close()
        return record

    def fetchone(self, query, tuple=None):
        connection = mysql.connector.connect(host=self.hostname,
                                             database=self.database,
                                             user=self.username,
                                             password=self.password)
        cur = connection.cursor()
        cur.execute(query, tuple)
        record = cur.fetchone()
        cur.close()
        return record


startsql = SQLstartup()

import xmltodict

from functions.filter_keys import filter_key
from functions.check_key_in_db import check_key_in_db
from functions.deprecated_functions.get_feed import get_hrk_xml
from helpers.db_connectv2 import startsql as sql
import pandas as pd
import logging
import time
import xml.etree.ElementTree as ET
log = logging.getLogger(__name__)
import urllib


async def get_hrk(game_name, game_id, args, store, user_cnf):
        def get_hrk_xml():
            url = 'https://www.hrkgame.com/nl/hotdeals/xml-feed/?key=F546F-DFRWE-DS3FV&cur=EUR'
            destination_file = 'hrk_xml.xml'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0'
            }

            request = urllib.request.Request(url, headers=headers)
            try:
                # Download the file
                with urllib.request.urlopen(request) as response, open(destination_file, 'wb') as out_file:
                    data = response.read()
                    out_file.write(data)

                print(f"File downloaded successfully to {destination_file}")

            except urllib.error.URLError as e:
                print(f"Failed to download the file. Error: {e}")

        with open('test.xml', 'r', encoding='utf-8') as xml_file:
            # Read the XML data from the file
            xml_data = xml_file.read()

            # Parse the XML data using xmltodict
            parsed_data = xmltodict.parse(xml_data)

            # Access the parsed data
            channel = parsed_data['rss']['channel']
            items = channel['item']

            for item in items:
                hrk_title = item['title']
                # Remove if function below to iterate over all items
                if args in hrk_title:
                    hrk_category = item['category']

                    # Check if category key exists and filter out DLCs
                    if hrk_category is None:
                        continue
                    if 'Downloadable Content' in hrk_category:
                        continue

                    hrk_id = item['g:id']
                    hrk_link = item['link']
                    hrk_price = item['g:price']
                    hrk_region = item['g:region']
                    hrk_steamid = item['steam_appid']
                    log.info(
                        f"hrk_id: {hrk_id}, hrk_title: {hrk_title}, hrk_link: {hrk_link}, hrk_price: {hrk_price}, hrk_region: {hrk_region}, hrk_steamid: {hrk_steamid}")
                else:
                    continue

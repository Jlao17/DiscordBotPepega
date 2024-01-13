import requests
import json
from functions.filter_keys import filter_key, filter_g2a
from functions.check_key_in_db import check_key_in_db
import time
from helpers.db_connectv2 import startsql as sql
import logging
import gzip
import requests
import gzip
from functions.filter_keys import filter_key

log = logging.getLogger(__name__)


async def get_fanatical(game_name, game_id, args, store, user_cnf):

    async def json_parse(name, counter):
        url = 'https://www.fanatical.com/feed.gz?apikey=22b1115e-e92d-4c4b-99d6-1f4230326ce7'
        # Download the gzip file
        response = requests.get(url)
        # Save the gzip file locally
        with open('data.gz', 'wb') as f:
            f.write(response.content)
        # Read the gzip file and extract its contents
        with gzip.open('data.gz', 'rb') as f:
            # Decode the gzip file contents
            file_content = f.read().decode('utf-8')
        # Split the content by newline characters
        lines = file_content.strip().split('\n')
        # Process each line separately as JSON
        for line in lines:
            # Parse the JSON data
            data = json.loads(line)
            # filter_result = filter_key(data["title"], name, data["url"], data["regular_price"])
            try:
                for uid in args["external_games"]:
                    if uid["category"] == 1:
                        if data["steam_app_id"] == int(uid["uid"]):
                            offer_url = data["url"]
                            try:
                                offer_price = data["coupon"]["price_after_coupon"]["EUR"]
                                offer_price_dollar = data["coupon"]["price_after_coupon"]["USD"]
                                offer_price_pound = data["coupon"]["price_after_coupon"]["GBP"]
                            except KeyError:
                                offer_price = data["current_price"]["EUR"]
                                offer_price_dollar = data["current_price"]["USD"]
                                offer_price_pound = data["current_price"]["GBP"]
                            # coupon price
                            offer_name = data["title"]

                            # Delete key is price or link is non-existing
                            if offer_url is None or offer_price is None:
                                log.info("offer rejected")
                                continue
                            else:
                                # if filter_g2a(offer_name, name):
                                # filter_result = filter_key(offer_name, name, "{}?ref=pricewatch"
                                #                            .format(offer_url), offer_price)
                                    price_list.append([offer_name, name, "{}?ref=pricewatch".format(offer_url),
                                                       offer_price, offer_price_dollar, offer_price_pound])
                                    await sql.execute(
                                        "INSERT INTO fanatical (id, key_name, fanatical_id, url, price, price_dollar, "
                                        "price_pound, last_modified) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                                        (game_id, offer_name, data["unique_game_id"], "{}?ref=pricewatch".format(offer_url),
                                         offer_price, offer_price_dollar, offer_price_pound, time.time()))
                                    counter += 1
                        else:
                            continue
            except KeyError:
                continue

                # else:
                #     print("offer deleted")
                #     continue
        return counter

    price_list = []
    # Same principle as check for 1st update steamdb
    result = await check_key_in_db(game_id, store)
    if result is None:
        count = 0
        try:
            count = await json_parse(game_name, count)
        except KeyError:
            log.exception(KeyError)
            return price_list
        # Try using IGDB game name instead
        if count == 0:
            count = await json_parse(args["name"], count)
        # If it's still 0, use alternative names
        # args
        #
        #
        #
        return price_list

    elif len(result) > 0:
        for entry in result:
            if int(time.time()) - int(entry[6]) > 43200:
                log.info("Longer than 12 hours")
                # game_data, app_name = get_steam_game(result[2])
                # Upload the new data in db here:
                # update_steamdb_game(game_data, result[2])
                return list(result)

            else:
                log.info("Less than 12 hours")
                return list(result)

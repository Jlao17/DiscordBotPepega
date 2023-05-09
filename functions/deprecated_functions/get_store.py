# import requests
# from functions.filter_keys import filter_key, filter_g2a
# from functions.check_key_in_db import check_key_in_db
# import time
# from helpers.db_connectv2 import startsql as sql
# import math
# from functions.get_steam_price import get_steam_price
# import discord
#
# browser_headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0"
# }
#
#
# async def get_g2a(game_name, app_name, game_id):
#     def json_request(name):
#         game_json = requests.get(
#             "https://www.g2a.com/search/api/v2/products?itemsPerPage=18&include[0]=filters&"
#             "currency=EUR&isWholesale=false&f[product-kind][0]=10&f[product-kind][1]=8&f[device][0]=1118&"
#             "f[regions][0]=8355&category=189&phrase=" + name, headers=browser_headers
#         ).json()
#         # print("https://www.g2a.com/search/api/v2/products?itemsPerPage=18&include[0]=filters&"
#         #       "currency=EUR&isWholesale=false&f[product-kind][0]=10&f[product-kind][1]=8&f[device][0]=1118&"
#         #       "f[regions][0]=8355&category=189&phrase=" + name)
#         return game_json
#
#     price_list = []
#     # Same principle as check for 1st update steamdb
#     result = await check_key_in_db(game_id, "g2a")
#
#     if result is None:
#         count = 0
#         game_json_g2a = json_request(game_name)
#         try:
#             for g2a_app in game_json_g2a["data"]["items"]:
#                 g2a_app_url = "https://www.g2a.com" + g2a_app["href"]
#                 g2a_app_price = g2a_app["price"]  # + g2a_app["currency"]
#                 g2a_app_name = g2a_app["name"]
#                 if filter_g2a(g2a_app_name, game_name):
#                     filter_result = filter_key(g2a_app_name, game_name, "{}?gtag=9b358ba6b1".format(g2a_app_url),
#                                                g2a_app_price)
#                     if filter_result is not None:
#                         price_list.append(filter_result)
#                         await sql.execute("INSERT INTO g2a (id, key_name, url, price, last_modified, g2a_id) VALUES "
#                                           "(%s, %s, %s, %s, %s, %s)",
#                                           (game_id, g2a_app_name, "{}?gtag=9b358ba6b1".format(g2a_app_url),
#                                            g2a_app_price, int(time.time()), g2a_app["id"]))
#                         count += 1
#                 else:
#                     continue
#         except KeyError:
#             print('KeyError in G2A' + KeyError)
#             return
#         if count == 0:
#             app_json_g2a = json_request(app_name)
#             for g2a_app in app_json_g2a["data"]["items"]:
#                 g2a_app_url = "https://www.g2a.com" + g2a_app["href"]
#                 g2a_app_price = g2a_app["price"]  # + g2a_app["currency"]
#                 g2a_app_name = g2a_app["name"]
#                 # Delete key is price or link is non-existing
#                 if g2a_app_url is None or g2a_app_price is None:
#                     continue
#                 else:
#                     if filter_g2a(g2a_app_name, game_name):
#                         filter_result = filter_key(g2a_app_name, game_name, "{}?gtag=9b358ba6b1"
#                                                    .format(g2a_app_url), g2a_app_price)
#                         if filter_result is not None:
#                             price_list.append(filter_result)
#                             await sql.execute(
#                                 "INSERT INTO G2A (id, key_name, g2a_id, url, price, last_modified) VALUES "
#                                 "(%s, %s, %s, %s, %s, %s)",
#                                 (game_id, g2a_app_name, g2a_app["id"], "{}?gtag=9b358ba6b1".format(g2a_app_url),
#                                  g2a_app_price, time.time()))
#         return price_list
#     elif len(result) > 0:
#         for entry in result:
#             if int(time.time()) - int(entry[4]) > 43200:
#                 print("Longer than 12 hours")
#                 # game_data, app_name = get_steam_game(result[2])
#                 # Upload the new data in db here:
#                 # update_steamdb_game(game_data, result[2])
#                 return None
#
#             else:
#                 print("Less than 12 hours")
#                 return list(result)
#
#
# async def get_kinguin(game_name, app_name, game_id):
#     price_list = []
#
#     def json_request(name):
#         game_json = requests.get(
#             "https://www.kinguin.net/services/library/api/v1/products/search?platforms=2,1,5,6,3,15,22,24,18,4,23&"
#             "productType=1&"
#             "countries=NL&"  # NL,US
#             "systems=Windows&"
#             "languages=en_US&"
#             "active=1&"
#             "hideUnavailable=0&"
#             "phrase=" + name + "&"
#                                "page=0&"
#                                "size=50&"
#                                "sort=bestseller.total,DESC&"
#                                "visible=1&"
#                                "lang=en_US&"
#                                "store=kinguin", headers=browser_headers
#         ).json()
#
#         return game_json
#
#     result = await check_key_in_db(game_id, "kinguin")
#     if result is None:
#         count = 0
#         game_json_kinguin = json_request(game_name)
#         try:
#             for kinguin_app in game_json_kinguin["_embedded"]["products"]:
#                 kinguin_app_url = "https://www.kinguin.net/category/" + \
#                                   str(kinguin_app["externalId"]) + "/" + \
#                                   kinguin_app["name"].replace(" ", "-")
#                 if kinguin_app["price"] is not None:
#                     kinguin_app_price = str(f"{kinguin_app['price']['lowestOffer'] / 100:.2f}")  # + "EUR"
#                     kinguin_app_name = kinguin_app["name"]
#
#                     filter_result = filter_key(kinguin_app_name, game_name, kinguin_app_url, kinguin_app_price)
#                     if filter_result is not None:
#                         price_list.append(filter_result)
#                         await sql.execute(
#                             "INSERT INTO kinguin (id, key_name, kinguin_id, url, price, last_modified) VALUES "
#                             "(%s, %s, %s, %s, %s, %s)",
#                             (game_id, kinguin_app_name, kinguin_app["id"], "{}".format(kinguin_app_url),
#                              kinguin_app_price, time.time()))
#                         count += 1
#                 else:
#                     continue
#         except KeyError:
#             print('KeyError in Kinguin' + KeyError)
#             return
#         if count == 0:
#             app_json_kinguin = json_request(app_name)
#             for kinguin_app in app_json_kinguin["_embedded"]["products"]:
#                 kinguin_app_url = "https://www.kinguin.net/category/" + \
#                                   str(kinguin_app["externalId"]) + "/" + \
#                                   kinguin_app["name"].replace(" ", "-")
#                 if kinguin_app["price"] is not None:
#                     kinguin_app_price = str(f"{kinguin_app['price']['lowestOffer'] / 100:.2f}")  # + "EUR"
#                     kinguin_app_name = kinguin_app["name"]
#                     filter_result = filter_key(kinguin_app_name, game_name, kinguin_app_url, kinguin_app_price)
#                     if filter_result is not None:
#                         price_list.append(filter_result)
#                         await sql.execute(
#                             "INSERT INTO kinguin (id, key_name, kinguin_id, url, price, last_modified) VALUES "
#                             "(%s, %s, %s, %s, %s, %s)",
#                             (game_id, kinguin_app_name, kinguin_app["id"], "{}".format(kinguin_app_url),
#                              kinguin_app_price, time.time()))
#         return price_list
#     elif len(result) > 0:
#         for entry in result:
#             if int(time.time()) - int(entry[4]) > 43200:
#                 print("Longer than 12 hours")
#                 # game_data, app_name = get_steam_game(result[2])
#                 # Upload the new data in db here:
#                 # update_steamdb_game(game_data, result[2])
#                 return None
#
#             else:
#                 print("Less than 12 hours")
#                 return list(result)
#
#
# async def get_k4g(game_name, app_name, game_id):
#     price_list = []
#
#     def json_request(name):
#         game_json = requests.get(
#             "https://k4g.com/api/v1/en/search/search?category_id=2&"
#             "platform[]=1&"
#             "platform[]=2&"
#             "platform[]=3&"
#             "platform[]=4&"
#             "platform[]=10&"
#             "platform[]=12&"
#             "product_type[]=1&"
#             "q={}&regions[]=1".format(name.replace(" ", "+")), headers=browser_headers
#         ).json()
#
#         return game_json
#
#     result = await check_key_in_db(game_id, "k4g")
#
#     if result is None:
#         count = 0
#         game_json_k4g = json_request(game_name)
#         try:
#             for k4g_app in game_json_k4g["items"]:
#                 k4g_app_url = "https://k4g.com/product/" + "-" + k4g_app["slug"] + "-" + str(k4g_app["id"])
#                 if k4g_app["featured_offer"] is not None:
#                     k4g_app_price = str(k4g_app["featured_offer"]["price"]["EUR"]["price"])  # + "EUR"
#                     k4g_app_name = k4g_app["title"]
#                     filter_result = filter_key(k4g_app_name, game_name, k4g_app_url, k4g_app_price)
#                     if filter_result is not None:
#                         price_list.append(filter_result)
#                         await sql.execute(
#                             "INSERT INTO k4g (id, key_name, k4g_id, url, price, last_modified) VALUES "
#                             "(%s, %s, %s, %s, %s, %s)",
#                             (game_id, k4g_app_name, k4g_app["id"], "{}?r=pricewatch".format(k4g_app_url),
#                              k4g_app_price, time.time()))
#                     count += 1
#                 else:
#                     continue
#         except KeyError:
#             print('KeyError in k4g' + KeyError)
#             return
#         if count == 0:
#             app_json_k4g = json_request(app_name)
#             for k4g_app in app_json_k4g["items"]:
#                 k4g_app_url = "https://k4g.com/product/" + "-" + k4g_app["slug"] + "-" + str(k4g_app["id"])
#                 if k4g_app["featured_offer"] is not None:
#                     k4g_app_price = str(k4g_app["featured_offer"]["price"]["EUR"]["price"])  # + "EUR"
#                     k4g_app_name = k4g_app["title"]
#                     filter_result = filter_key(k4g_app_name, game_name, k4g_app_url, k4g_app_price)
#                     if filter_result is not None:
#                         price_list.append(filter_result)
#                         await sql.execute(
#                             "INSERT INTO k4g (id, key_name, k4g_id, url, price, last_modified) VALUES "
#                             "(%s, %s, %s, %s, %s, %s)",
#                             (game_id, k4g_app_name, k4g_app["id"], "{}?r=pricewatch".format(k4g_app_url),
#                              k4g_app_price, time.time()))
#         return price_list
#
#     elif len(result) > 0:
#         for entry in result:
#             if int(time.time()) - int(entry[4]) > 43200:
#                 print("Longer than 12 hours")
#                 # game_data, app_name = get_steam_game(result[2])
#                 # Upload the new data in db here:
#                 # update_steamdb_game(game_data, result[2])
#                 return None
#
#             else:
#                 print("Less than 12 hours")
#                 return list(result)
#
#
# def gamivo(steam_game):
#     pass

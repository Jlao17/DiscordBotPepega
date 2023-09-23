import requests

regions = {"global": ["1"], "eu": ["1", "2"], "na": ["1", "6"]}
url = "https://search.driffle.com/products/v2/list?limit=54&productType=game,dlc&region=3&page=1&q=dead+by+daylight"


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
}

game_json = requests.request("GET", url, headers=headers).json()

print(game_json)
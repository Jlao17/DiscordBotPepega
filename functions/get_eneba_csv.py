import requests

def get_eneba_csv():
    print("start feed parsing")
    url = "https://www.eneba.com/rss/products.csv?version=3&af_id=PriceWatch"
    with requests.Session() as s:
        download = s.get(url)

        url_content = download.content
        csv_file = open('eneba_csv.csv', 'ab')
        csv_file.write(url_content)
        csv_file.close()
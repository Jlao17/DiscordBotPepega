import requests
import logging

log = logging.getLogger(__name__)


async def get_eneba_csv():
    log.info("start feed parsing")
    url = "https://www.eneba.com/rss/products.csv?version=3&af_id=PriceWatch"
    with requests.Session() as s:
        download = s.get(url)
        url_content = download.content
        csv_clear = open('eneba_csv.csv', 'w')
        csv_clear.close()
        csv_file = open('eneba_csv.csv', 'ab')
        csv_file.write(url_content)
        csv_file.close()


async def get_hrk_xml():
    log.info("start feed parsing")
    url = "https://www.hrkgame.com/en/hotdeals/xml-feed/?key=F546F-DFRWE-DS3FV&cur=EUR"
    with requests.Session() as s:
        download = s.get(url)
        url_content = download.content
        csv_clear = open('hrk_xml.xml', 'w')
        csv_clear.close()
        csv_file = open('hrk_xml.xml', 'ab')
        csv_file.write(url_content)
        csv_file.close()

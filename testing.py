import pandas as pd
import lxml
import requests
import logging as log

# log.info("start feed parsing")
# url = "https://www.hrkgame.com/en/hotdeals/xml-feed/?key=F546F-DFRWE-DS3FV&cur=EUR"
# with requests.Session() as s:
#     download = s.get(url)
#     url_content = download.content
#     csv_clear = open('hrk_xml.xml', 'w')
#     csv_clear.close()
#     csv_file = open('hrk_xml.xml', 'ab')
#     csv_file.write(url_content)
#     csv_file.close()

# df = pd.read_xml('hrk_xml.xml')
#
# print(df)

import xml.etree.ElementTree as ET
import pandas as pd


def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    return root


def extract_data(root):
    data = []
    for channel in root:
        for item in channel:
            row = {}
            for attr in item:
                column_name = attr.tag
                column_value = attr.text
                if "{http://base.google.com/ns/1.0}" in attr.tag:
                    clean_column_name= column_name.replace("{http://base.google.com/ns/1.0}", "")
                    row[clean_column_name] = column_value
                else:
                    row[column_name] = column_value
            data.append(row)
    return data


def to_dataframe(data):
    df = pd.DataFrame(data)
    return df


def to_csv(df, filename):
    df.to_csv(filename, index=False)


def main(xml_file, csv_file):
    root = parse_xml(xml_file)
    data = extract_data(root)
    df = to_dataframe(data)
    to_csv(df, csv_file)


if __name__ == "__main__":
    main('hrk_xml.xml', 'data.csv')

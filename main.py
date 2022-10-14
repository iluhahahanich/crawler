import argparse

import requests as req
from bs4 import BeautifulSoup
import pandas as pd


class Crawler:
    def __init__(self):
        self.columns = ['Product name', 'Brand name', 'Price', 'Main image url',
                        'Product Overview', 'How to Use']

        self.data = pd.DataFrame(columns=self.columns)

    def parse(self, url):
        resp = req.get(url)
        if not resp.ok:
            return

        soup = BeautifulSoup(resp.text, features='html.parser')

        name_n_brand = self._parse_name_and_brand(soup)
        price = self._parse_price(soup)
        img_url = self._parse_img_url(soup)
        descriptions = self._parse_descriptions(soup, desc_columns=self.columns[-2:])

        result = {**name_n_brand, **price, **img_url, **descriptions}

        self.data = self.data.append(result, ignore_index=True)

    def write(self, filename):
        self.data[self.columns].to_csv(filename, index=False)

    @staticmethod
    def _parse_name_and_brand(soup):
        header = soup.find('div', attrs={'class': 'athenaProductPage_titleTagFirst'})
        name = header.find(attrs={'class': 'productName_title'}).text
        brand = header.find(attrs={'class': 'productBrandLogo_image'})['alt']
        return {'Product name': name, 'Brand name': brand}

    @staticmethod
    def _parse_price(soup):
        price = soup.find(attrs={'class': 'productPrice_priceAmount'}).text
        return {'Price': float(price)}

    @staticmethod
    def _parse_img_url(soup):
        img_url = soup.find(attrs={'class': 'athenaProductImageCarousel_imageSlider'}).find('img')['src']
        return {'Main image url': img_url}

    @staticmethod
    def _parse_descriptions(soup, desc_columns):
        result = {}
        descriptions = soup.find_all('div', {'class': 'productDescription_contentPropertyListItem'})
        for desc in descriptions:
            name = desc.find('div', attrs={'class': 'productDescription_contentPropertyHeading'}).text.strip()
            if name not in desc_columns[-2:]:
                continue

            description = desc.find('div', attrs={'class': 'athenaProductPageSynopsisContent'}).text

            result[name] = description

        return result


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', required=True, help='url to parse')
    parser.add_argument('-o', '--out', help='file to write parsing result')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    c = Crawler()
    c.parse(args.url)

    c.write(args.out or 'data.csv')


if __name__ == '__main__':
    main()

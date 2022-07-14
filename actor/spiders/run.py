import json
import re
import os
import apify
import logging
from scrapy import Spider
from urllib.parse import urljoin
from apify_client import ApifyClient
from scrapy.http.request import Request


class amazon_products_reviews(Spider):

    name = 'humblebundle_bundles'

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
               'Accept-Language': 'en-US,en;q=0.5',
               'Upgrade-Insecure-Requests': '1',
               'Sec-Fetch-Dest': 'document',
               'Sec-Fetch-Mode': 'navigate',
               'Sec-Fetch-Site': 'none',
               'Sec-Fetch-User': '?1',}

    client = None

    logger = None

    directory_path = os.getcwd()

    env = os.getenv("SCRAPY_ENV")

    scrape_bundles = True

    scrapers_urls = {'bundles': 'https://www.humblebundle.com/bundles'}

    client = None

    def start_requests(self):

        self.logger = logging.getLogger()

        if self.env is None:

            # Initialize the main ApifyClient instance
            client = ApifyClient(os.environ['APIFY_TOKEN'], api_url=os.environ['APIFY_API_BASE_URL'])

            # Get the resource subclient for working with the default key-value store of the actor
            default_kv_store_client = client.key_value_store(os.environ['APIFY_DEFAULT_KEY_VALUE_STORE_ID'])

            # Get the value of the actor input and print it
            self.logger.info('Loading input...')
            actor_input = default_kv_store_client.get_record(os.environ['APIFY_INPUT_KEY'])['value']
            self.logger.info(actor_input)

            self.scrape_bundles = actor_input["scrape_bundles"]

        if self.scrape_bundles:
            url = self.scrapers_urls['bundles']
            yield Request(url=url,
                          callback=self.parse_overview_page)

    def parse_overview_page(self, response):

        json_results = response.xpath('.//script[@id="landingPage-json-data"]/text()')
        if json_results and len(json_results) > 0:
            json_results = json_results.extract()[0].strip()
            json_results = json.loads(json_results)

            books = json_results['data']['books']['mosaic'][0]['products']
            games = json_results['data']['games']['mosaic'][0]['products']
            software = json_results['data']['software']['mosaic'][0]['products']

            data = {'books': books,
                    'games': games,
                    'software': software}

            if self.env is None:
                apify.pushData(data)
            else:
                yield data

import unittest

import weakscraper
from weakscraper import exceptions

class TestWPName(unittest.TestCase):
    def setUp(self):
        template_string = """
            <!DOCTYPE html>
            <html>
                <head wp-name="head">
                    <title wp-name="title"/>
                </head>
            </html>
            """

        self.scraper = weakscraper.WeakScraper(template_string)


    def test_match(self):
        content = """
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Title</title>
                </head>
            </html>
            """

        result_data = self.scraper.scrap(content)

        self.assertEqual(result_data, {'head': {'title': 'Title'}})

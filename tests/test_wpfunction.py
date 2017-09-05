import unittest

import weakscraper
from weakscraper import exceptions

class TestWPFunction(unittest.TestCase):
    def setUp(self):
        template_string = """
            <!DOCTYPE html>
            <html>
                <head wp-function="sum">
                    <number wp-name="a" wp-function="int"/>
                    <number wp-name="b" wp-function="int"/>
                </head>
            </html>
            """

        functions = {
            'int': int,
            'sum': (lambda dic: dic['a'] + dic['b'])
        }

        self.scraper = weakscraper.WeakScraper(template_string, functions)


    def test_sum(self):
        content = """
            <!DOCTYPE html>
            <html>
                <head>
                    <number>
                        12
                    </number>
                    <number>
                        -5
                    </number>
                </head>
            </html>
            """

        result_data = self.scraper.scrap(content)

        self.assertEqual(result_data, {'sum': 7})

import unittest

import weakscraper
from weakscraper import exceptions

class TestWPList(unittest.TestCase):
    def setUp(self):
        template_string = """
            <!DOCTYPE html>
            <html>
                <body>
                    <div wp-function="sum" wp-list>
                        <number wp-name="number" wp-function="int"/>
                    </div>
                    <number wp-function="str_sum" wp-list/>
                </body>
            </html>
            """

        functions = {
            'int': int,
            'sum': (lambda l: sum([n['sum']['number'] for n in l])),
            'str_sum': (lambda l: sum([int(n['str_sum']) for n in l]))
        }


        self.scraper = weakscraper.WeakScraper(template_string, functions)



    def test_empty(self):
        content = """
            <!DOCTYPE html>
            <html>
                <body>
                </body>
            </html>
            """

        result_data = self.scraper.scrap(content)

        self.assertEqual(result_data, {'sum': 0, 'str_sum': 0})


    def test_sum(self):
        content = """
            <!DOCTYPE html>
            <html>
                <body>
                    <div>
                        <number>12</number>
                    </div>
                    <div>
                        <number>-5</number>
                    </div>
                    <number>1</number>
                    <number>2</number>
                    <number>3</number>
                </body>
            </html>
            """

        result_data = self.scraper.scrap(content)

        self.assertEqual(result_data, {'sum': 7, 'str_sum': 6})

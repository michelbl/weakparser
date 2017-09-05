import unittest

import weakscraper
from weakscraper import exceptions

class TestWPNugget(unittest.TestCase):
    def setUp(self):
        template_string = """
            <!DOCTYPE html>
            <html>
                <body>
                    <tag1>begining<wp-nugget wp-name="info1"/>middle<wp-nugget wp-name="info2"/>end</tag1>
                    <tag2><wp-nugget wp-name="info3"/>end</tag2>
                </body>
            </html>
            """

        self.scraper = weakscraper.WeakScraper(template_string)


    def test_1(self):
        content = """
            <!DOCTYPE html>
            <html>
                <body>
                    <tag1>beginingABCmiddleDEFend</tag1>
                    <tag2>GHIend</tag2>
                </body>
            </html>
            """

        result_data = self.scraper.scrap(content)

        self.assertEqual(result_data, {'info1': 'ABC', 'info2': 'DEF', 'info3': 'GHI'})

import unittest

import weakscraper
from weakscraper import exceptions

class TestWPIgnore(unittest.TestCase):
    def setUp(self):
        template_string = """
            <!DOCTYPE html>
            <html>
                <body>
                    <tag1>a</tag1>
                    <wp-ignore wp-until="tag4"/>
                    <tag4 attr1="value" wp-ignore-attrs>b</tag4>
                    <tag5 wp-ignore-content/>
                    <tag6 wp-ignore/>
                    <wp-ignore/>
                </body>
            </html>
            """

        self.scraper = weakscraper.WeakScraper(template_string)


    def test_until(self):
        content = """
            <!DOCTYPE html>
            <html>
                <body>
                    <tag1>a</tag1>
                    <tag2><tag21>some text</tag21></tag2>
                    <tag3></tag3>
                    <tag4 attr1="value">b</tag4>
                    <tag5></tag5>
                    <tag6></tag6>
                </body>
            </html>
            """

        result_data = self.scraper.scrap(content)

        self.assertEqual(result_data, {})


    def test_attr(self):
        content = """
            <!DOCTYPE html>
            <html>
                <body>
                    <tag1>a</tag1>
                    <tag4 attr2="value" attr1="value">b</tag4>
                    <tag5></tag5>
                    <tag6></tag6>
                </body>
            </html>
            """

        result_data = self.scraper.scrap(content)

        self.assertEqual(result_data, {})


    def test_content(self):
        content = """
            <!DOCTYPE html>
            <html>
                <body>
                    <tag1>a</tag1>
                    <tag4 attr1="value">b</tag4>
                    <tag5>some random text</tag5>
                    <tag6></tag6>
                </body>
            </html>
            """

        result_data = self.scraper.scrap(content)

        self.assertEqual(result_data, {})


    def test_attr_and_content(self):
        content = """
            <!DOCTYPE html>
            <html>
                <body>
                    <tag1>a</tag1>
                    <tag4 attr1="value">b</tag4>
                    <tag5></tag5>
                    <tag6 randomattr="value">
                        <tag61>random content</tag61>
                        <tag62>random content</tag62>
                    </tag6>
                </body>
            </html>
            """

        result_data = self.scraper.scrap(content)

        self.assertEqual(result_data, {})


    def test_ignore(self):
        content = """
            <!DOCTYPE html>
            <html>
                <body>
                    <tag1>a</tag1>
                    <tag4 attr1="value">b</tag4>
                    <tag5></tag5>
                    <tag6></tag6>
                    <tag7><tag71></tag71></tag7>
                    <tag8></tag8>
                </body>
            </html>
            """

        result_data = self.scraper.scrap(content)

        self.assertEqual(result_data, {})

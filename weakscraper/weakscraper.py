# -*- coding: utf-8 -*-

# our apps
from weakscraper.template import Template
from weakscraper.htmlparser import HtmlParser
from weakscraper.templateparser import TemplateParser


class WeakScraper:
    def __init__(self, template_string, functions=None):
        template_parser = TemplateParser()
        template_parser.feed(template_string)
        tpl_tree = template_parser.get_result()

        self.template = Template(tpl_tree, functions)

    def scrap(self, html):
        html_parser = HtmlParser()
        html_parser.feed(html)
        html_tree = html_parser.get_result()

        results = self.template.compare(html_tree)
        return results

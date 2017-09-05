# -*- coding: utf-8 -*-

# python apps
import html.parser
from abc import ABCMeta

# out apps
from .exceptions import AssertCompleteFailure

DEBUG = False


class BaseParser(html.parser.HTMLParser, metaclass=ABCMeta):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.genealogy = [[]]

    def __str__(self):
        return '<BaseParser(genealogy={})>'.format(self.genealogy)

    def assert_complete(self):
        assert(len(self.genealogy) == 1)
        root_node = None
        for root_node in self.genealogy[0]:
            if root_node['nodetype'] == 'tag' and root_node['name'] == 'html':
                break
        if not root_node:
            raise AssertCompleteFailure(self.genealogy)
        return root_node

    def get_result(self):
        root_node = self.assert_complete()
        return root_node

    def handle_startendtag(self, tag, attrs):
        attrs.append(('wp-leaf', None))
        self.handle_starttag(tag, attrs)

    def handle_data(self, text):
        text = text.strip(' \t\n\r')
        if text:
            brothers = self.genealogy[-1]
            myself = {'nodetype': 'text', 'content': text}
            brothers.append(myself)

    def handle_decl(self, decl):
        arr = decl.lower().split()
        if arr:
            self.handle_starttag(arr[0], [('wp-decl', None)])

    def unknown_decl(self, data):
        self.handle_decl(data)

    def handle_starttag(self, tag, attrs):
        raise NotImplementedError('action must be defined!')

    def handle_endtag(self, tag):
        raise NotImplementedError('action must be defined!')



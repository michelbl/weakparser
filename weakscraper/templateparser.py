# -*- coding: utf-8 -*-

# our apps
from weakscraper.base_parser import BaseParser
from weakscraper.exceptions import EndTagError


class TemplateParser(BaseParser):
    def __str__(self):
        return '<TemplateParser(genealogy={})>'.format(self.genealogy)

    def handle_starttag(self, tag, attrs):
        attrs_dict = {}
        params = {}
        possible_params = [
                'wp-decl', 'wp-leaf',
                'wp-name', 'wp-recursive', 'wp-list', 'wp-function',
                'wp-optional', 'wp-until',
                'wp-ignore', 'wp-ignore-attrs', 'wp-ignore-content',
                'wp-name-attrs', 'wp-function-attrs',
                ]

        if tag in ('meta', 'img', 'hr', 'br') and 'wp-leaf' not in attrs:
            attrs.append(('wp-leaf', None))

        for k, v in attrs:
            if k in possible_params:
                if k == 'wp-ignore':
                    params['wp-ignore-content'] = None
                    params['wp-ignore-attrs'] = None
                elif k == 'wp-recursive-leaf':
                    params['wp-leaf'] = None
                    params['wp-recursive-leaf'] = None
                else:
                    params[k] = v
            elif k in attrs_dict:
                raise ValueError('Attribute defined multiple times in tag.')
            else:
                attrs_dict[k] = v

        brothers = self.genealogy[-1]

        node = {
                'nodetype': 'tag',
                'name': tag,
                'attrs': attrs_dict,
                'params': params,
                'children': [],
                }
        brothers.append(node)

        if not any((s in node['params'] for s in ('wp-leaf', 'wp-decl'))):
            self.genealogy.append(node['children'])

    def handle_endtag(self, tag):
        parent = self.genealogy[-2][-1]

        if (parent['nodetype'] != 'tag'):
            raise EndTagError(self.genealogy, parent['nodetype'])
        elif (parent['name'] != tag):
            raise EndTagError(self.genealogy, parent['name'])
        else:
            self.genealogy.pop()


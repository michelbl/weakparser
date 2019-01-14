import collections
import html.parser

from weakscraper import exceptions


class HtmlParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)

        self.genealogy = []
        self.genealogy.append([])

    def assert_complete(self):
        assert(len(self.genealogy) == 1)
        if len(self.genealogy[0]) != 1:
            raise exceptions.AssertCompleteFailure(self.genealogy)
        root_node = self.genealogy[0][0]
        assert(root_node['nodetype'] == 'tag')
        assert(root_node['name'] == 'html')

    def get_result(self):
        self.assert_complete()
        root_node = self.genealogy[0][0]
        return root_node

    def feed(self, data):
        super().feed(data)

    def reset(self):
        super().reset()

    def handle_starttag(self, tag, attrs):
        attrs_dict = {}
        is_leaf = False
        is_decl = False
        for k, v in attrs:
            if k == 'wp-leaf':
                is_leaf = True
            elif k == 'wp-decl':
                is_decl = True
            else:
                attrs_dict[k] = v

        if tag in ['meta', 'link', 'br', 'img', 'input']:
            is_leaf = True

        if tag == 'html':
            if not is_decl:
                is_leaf = True

        brothers = self.genealogy[-1]

        if is_leaf:
            node = {'nodetype': 'tag', 'name': tag, 'attrs': attrs_dict}
            brothers.append(node)
        else:
            children = []
            node = {'nodetype': 'tag', 'name': tag, 'attrs': attrs_dict,
                'children': children}
            brothers.append(node)
            self.genealogy.append(node['children'])

    def handle_endtag(self, tag):
        parent = self.genealogy[-2][-1]

        if (parent['nodetype'] != 'tag'):
            raise exceptions.NodeTypeDiscrepancy(self.genealogy,
                parent['nodetype'])
        if (parent['name'] != tag):
            raise exceptions.EndTagDiscrepancy(self.genealogy,
                parent['name'])

        self.genealogy.pop()

    def handle_startendtag(self, tag, attrs):
        attrs.append(('wp-leaf', None))
        self.handle_starttag(tag, attrs)

    def handle_data(self, text):
        text = text.strip(' \t\n\r')
        if text:
            brothers = self.genealogy[-1]
            myself = {'nodetype': 'text', 'content': text}
            brothers.append(myself)

    def handle_entityref(self, name):
        raise AssertionError('This portion of code should never be reached.')

    def handle_charref(self, name):
        raise AssertionError('This portion of code should never be reached.')

    def handle_comment(self, text):
        # ignore comments !
        pass

    def handle_decl(self, decl):
        self.handle_starttag(tag='html', attrs=[('wp-decl', None)])

    def handle_pi(self, decl):
        raise AssertionError('PI.')

    def unknown_decl(self, data):
        raise ValueError('Unknown declaration.')

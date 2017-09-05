# -*- coding: utf-8 -*-

# python apps
import re

# our apps
from weakscraper import exceptions
from weakscraper.exceptions import (
        AttrsError, CompareError, ExcessNodeError, MissingNodeError,
        NonAtomicChildError, NodetypeError, TagError, TextError,
        TextExpectedError,
        )


def _html_children_skip(info, i, n):
    while i < n and info[i]['nodetype'] == 'tag' and info[i]['name'] == 'script':
        i += 1
    return i


def _html_children_until(tpl_child, info, i, n):
    '"wp-until" in tpl_child.params'
    until = tpl_child.params['wp-until']
    while i < n and not (info[i]['nodetype'] == 'tag' and info[i]['name'] == until):
        i += 1
    return i


def _html_children_tag(obj, tpl_child, html, i, n, children_results):
    'tpl_child.nodetype in ["nugget", "texts-and-nuggets", "tag"]'
    info = html['children']
    if not (
            tpl_child.nodetype == 'tag'
            and 'wp-optional' in tpl_child.params
            and not _check_flag(tpl_child, info, i, n)
            ):
        if i >= n:
            e = MissingNodeError(tpl_child, html)
            e.register_parent(obj)
            raise e
        result = obj._compare_wrapper(tpl_child, info[i])
        for k, v in result.items():
            if k in children_results:
                raise ValueError('Key already defined.')
            children_results[k] = v
        i += 1
    return i


def _html_children_wp_list(obj, tpl_child, info, i, n, children_results):
    'tpl_child.nodetype == "tag" and "wp-list" in tpl_child.params'
    arr = []
    while _check_flag(tpl_child, info, i, n):
        x = obj._compare_wrapper(tpl_child, info[i])
        arr.append(x)
        i += 1
    name = tpl_child.params['wp-name']
    if 'wp-function' in tpl_child.params:
        function_name = tpl_child.params['wp-function']
        function = obj.functions[function_name]
        arr = function(arr)
    children_results[name] = arr
    return (i, children_results)


def _check_flag(tpl_child, info, i, n):
    flag = (
            i < n
            and info[i]['nodetype'] == 'tag'
            and info[i]['name'] == tpl_child.name
            and tpl_child._attrs_match(info[i]['attrs'])
            )
    return flag


def _check_text_flag(tpl_childrens):
    arr = []
    for child in tpl_childrens:
        assert child['nodetype'] in ('text', 'tag')

        if child['nodetype'] == 'text' or child['name'] == 'wp-nugget':
            flag = True
        else:
            flag = False
        arr.append(flag)
    return arr


class Template:
    def __repr__(self):
        keys = (
                'nodetype', 'name', 'names', 'attrs', 'children',
                'functions', 'params',
                )
        arr = []
        for key in keys:
            if hasattr(self, key):
                value = getattr(self, key)
                if isinstance(value, str):
                    value = '"{}"'.format(value)
                s = '{}={}'.format(key, value)
                arr.append(s)
        ret = '<Template({})>'.format(', '.join(arr))
        return ret

    def __init__(self, raw_template, functions):
        self.functions = functions

        if raw_template['nodetype'] == 'tag':
            self._init_tag(raw_template)
        elif raw_template['nodetype'] == 'texts-and-nuggets':
            self._init_texts_and_nuggets(raw_template)
        else:
            msg = 'Unknown nodetype {}.'.format(raw_template['nodetype'])
            raise ValueError(msg)

    def _process_grandchildren(self, arr):
        text_template = {
                'nodetype': 'texts-and-nuggets',
                'children': arr,
                }
        new_child = Template(text_template, self.functions)
        self.children.append(new_child)

    def _init_tag(self, raw_template):
        tag = raw_template['name']
        assert(tag != 'wp-nugget')

        if tag == 'wp-ignore':
            self.nodetype = 'ignore'
            self.params = raw_template['params']
            return

        self.nodetype = 'tag'
        self.name = raw_template['name']
        self.attrs = raw_template['attrs']
        self.params = raw_template['params']

        if 'wp-function' in self.params and 'wp-name' not in self.params:
            self.params['wp-name'] = self.params['wp-function']

        if 'wp-function-attrs' in self.params \
                and 'wp-name-attrs' not in self.params:
            self.params['wp-name-attrs'] = self.params['wp-function-attrs']

        if 'wp-name-attrs' in self.params:
            self.params['wp-ignore-attrs'] = None

        if 'wp-ignore-content' in self.params:
            del self.params['wp-leaf']
            ignore = Template(
                    {'nodetype': 'tag', 'name': 'wp-ignore', 'params': {}},
                    self.functions,
                    )
            self.children = [ignore]
            return

        if 'wp-leaf' in self.params:
            assert(len(raw_template['children']) == 0)
            return

        text_flags = _check_text_flag(raw_template['children'])

        self.children = []
        grandchildren = []
        for i, child in enumerate(raw_template['children']):
            if text_flags[i]:
                grandchildren.append(child)
            else:
                if grandchildren:
                    self._process_grandchildren(grandchildren)
                    grandchildren = []
                new_child = Template(child, self.functions)
                self.children.append(new_child)
        if grandchildren:
            self._process_grandchildren(grandchildren)
            grandchildren = []

    def _init_texts_and_nuggets(self, raw_template):
        if len(raw_template['children']) == 1:
            child = raw_template['children'][0]
            if child['nodetype'] == 'text':
                self.nodetype = 'text'
                self.content = child['content']

            elif child['nodetype'] == 'tag':
                assert(child['name'] == 'wp-nugget')
                self.nodetype = 'nugget'
                self.params = child['params']

            else:
                raise ValueError('Unexpected nodetype.')
            return

        self.nodetype = 'texts-and-nuggets'
        self.regex = ''
        self.names = []
        self.functions = []

        expected_type = raw_template['children'][0]['nodetype']
        for child in raw_template['children']:
            if child['nodetype'] != expected_type:
                raise ValueError('Unexpected nodetype.')

            elif child['nodetype'] == 'text':
                self.regex += re.escape(child['content'])
                expected_type = 'tag'

            elif child['nodetype'] == 'tag':
                self.regex += '(.*)'
                name = child['params']['wp-name']
                self.names.append(name)
                if 'wp-function' in child['params']:
                    function = child['params']['wp-function']
                else:
                    function = None
                self.functions.append(function)
                expected_type = 'text'

            else:
                raise ValueError('Unexpected nodetype.')

    def _f(self, obj):
        'self.nodetype == "tag"'
        if 'wp-function' in self.params and 'wp-list' not in self.params:
            function_name = self.params['wp-function']
            function = self.functions[function_name]
            return function(obj)
        else:
            return obj

    def _compare_wrapper(self, tpl_child, html):
        try:
            results = tpl_child.compare(html)
        except CompareError as e:
            e.register_parent(self)
            raise e
        return results

    def compare(self, html):
        results = {}

        if self.nodetype == 'text':
            self._compare__text(html)
        elif self.nodetype == 'nugget':
            self._compare__nugget(html, results)
        elif self.nodetype == 'texts-and-nuggets':
            self._compare__texts_and_nuggets(html, results)
        elif 'children' not in html:
            pass
        elif self.nodetype == 'tag':
            self._compare__tag(html, results)
        else:
            raise ValueError('Unexpected nodetype.')
        return results

    def _compare__text(self, html):
        'self.nodetype == "text"'
        if html['nodetype'] != 'text':
            raise NodetypeError(self, html)
        if html['content'] != self.content:
            raise TextError(self, html)

    def _compare__nugget(self, html, results):
        'self.nodetype == "nugget"'
        content = self._f(html['content'])

        name = self.params['wp-name']
        results[name] = content

    def _compare__texts_and_nuggets(self, html, results):
        'self.nodetype == "texts-and-nuggets"'
        regex = '^' + self.regex + '$'
        match = re.match(regex, html['content'])
        groups = match.groups()
        assert(len(groups) == len(self.names))
        assert(len(groups) == len(self.functions))

        for i in range(len(groups)):
            name = self.names[i]
            function_name = self.functions[i]
            result = groups[i]
            if function_name:
                function = self.functions[function_name]
                result = function(result)
            results[name] = result

    def _compare__tag(self, html, results):
        'self.nodetype == "tag"'
        if (html['nodetype'] != 'tag'):
            raise NodetypeError(self, html)
        elif (self.name != html['name']):
            raise TagError(self, html)
        elif not self._attrs_match(html['attrs']):
            raise AttrsError(self, html)

        if 'wp-name-attrs' in self.params:
            self._tpl__wp_name_attrs(html, results)

        if 'wp-leaf' in self.params:
            self._tpl__wp_leaf(html, results)
        else:
            # look at the children
            self._tpl__children(html, results)

    def _tpl__wp_name_attrs(self, html, results):
        name = self.params['wp-name-attrs']
        content = html['attrs']
        if 'wp-function-attrs' in self.params:
            function_name = self.params['wp-function-attrs']
            function = self.functions[function_name]
            content = function(content)
        results[name] = content

    def _tpl__wp_leaf(self, html, results):
        if 'wp-recursive' in self.params:
            name = self.params['wp-name']
            results[name] = self._f(html['children'])
        elif 'wp-ignore-content' not in self.params:
            if 'wp-name' in self.params:
                try:
                    name = self.params['wp-name']
                    if len(html['children']) == 0:
                        content = ''
                    elif len(html['children']) == 1:
                        html_child = html['children'][0]
                        if html_child['nodetype'] != 'text':
                            raise TextExpectedError(self, html_child)
                        content = html_child['content']
                    else:
                        raise NonAtomicChildError(self, html)
                    results[name] = self._f(content)
                except NonAtomicChildError:
                    # html['children']与tpl['children']不匹配
                    results[name] = html['children']
            else:
                assert('children' not in html)

    def _tpl__children(self, html, results):
        'traversal tag children of template'
        children_results = {}
        info = html['children']

        html_i = 0
        html_n = len(info)

        for tpl_child in self.children:
            html_i = _html_children_skip(info, html_i, html_n)

            if tpl_child.nodetype == 'ignore':
                if 'wp-until' in tpl_child.params:
                    html_i = _html_children_until(tpl_child, info, html_i,
                            html_n)
                else:
                    html_i = html_n
            elif tpl_child.nodetype == 'tag' and 'wp-list' in tpl_child.params:
                html_i, children_results = _html_children_wp_list(self,
                        tpl_child, info, html_i, html_n, children_results)
            elif tpl_child.nodetype == 'text':
                self._compare_wrapper(tpl_child, info[html_i])
                html_i += 1
            elif tpl_child.nodetype in ('nugget', 'texts-and-nuggets', 'tag'):
                html_i = _html_children_tag(self, tpl_child, html, html_i,
                        html_n, children_results)
            else:
                raise ValueError('Unknown child type.')

        html_i = _html_children_skip(info, html_i, html_n)

        if html_i != html_n:
            raise ExcessNodeError(self, info[html_i])

        if 'wp-name' in self.params:
            name = self.params['wp-name']
            results[name] = self._f(children_results)
        else:
            for k, v in children_results.items():
                if k in results:
                    raise ValueError('Key already defined.')
                results[k] = v

    def _attrs_match(self, html_attrs):
        ret = True
        if 'wp-ignore-attrs' not in self.params:
            ret = self.attrs == html_attrs
        else:
            for key, value in self.attrs.items():
                if key not in html_attrs or html_attrs[key] != value:
                    ret = False
                    break
        return ret


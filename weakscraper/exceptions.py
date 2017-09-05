import collections
import json



def genealogy_pretty_output(genealogy):
    message = ''

    for l in genealogy:
        message += '  '
        if l:
            node = l[-1]
            node_string = str({k: v for k, v in node.items() if k != 'children'})
            if len(node_string) > 160:
                message += node_string[:160] + '...'
            else:
                message += node_string
            message += '"'
            message += '\n'

    return message


class ParsingError(Exception):
    def __init__(self, template_genealogy, html_element=None):
        self.template_genealogy = template_genealogy
        self.html_element = html_element

        if self.html_element:
            self.html_str = self.html2str(self.html_element)

    def html2str(self, html_element):
        return str(html_element)

    def __str__(self):
        message = ''
        message += self.__class__.__name__ + ' detected !\n'

        message += 'Template genealogy : \n'
        message += genealogy_pretty_output(self.template_genealogy)

        if self.html_element:
            message += 'Conflicting Html element : \n'
            message += '  ' + self.html_str + '\n'
        return message


class EndTagError(ParsingError):
    pass

class AssertCompleteFailure(ParsingError):
    pass


class EndTagDiscrepancy(ParsingError):
    pass


class NodeTypeDiscrepancy(ParsingError):
    pass


class CompareError(Exception):
    def __init__(self, template, html):
        self.html = html
        self.genealogy = collections.deque([template])

    def register_parent(self, template):
        self.genealogy.appendleft(template)

    def __str__(self):
        message = ''
        message += self.__class__.__name__ + ' detected !\n'

        message += 'Template genealogy : \n'
        for template in self.genealogy:
            message += '  ' + template.nodetype + ' : '
            if hasattr(template, 'name'):
                message += 'name='
                message += str(template.name)
                message += '; '
            if hasattr(template, 'params'):
                message += 'params='
                message += str(template.params)
                message += ';'
            if hasattr(template, 'attrs'):
                message += 'attrs='
                message += str(template.attrs)
                message += ';'
            message += '\n'

        message += 'Html element : \n'
        message += json.dumps(self.html, indent=2)

        return message


class NodetypeError(CompareError):
    pass

class TextExpectedError(CompareError):
    pass

class TagError(CompareError):
    pass

class AttrsError(CompareError):
    pass

class TextError(CompareError):
    pass

class ExcessNodeError(CompareError):
    pass

class MissingNodeError(CompareError):
    pass

class NonAtomicChildError(CompareError):
    pass

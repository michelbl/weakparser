# weakscraper
HTML scraper with templates

[![Python version](https://img.shields.io/pypi/pyversions/weakscraper.svg)](https://www.python.org/download/releases/3.0/)
[![PyPI version](https://badge.fury.io/py/weakscraper.svg)](https://badge.fury.io/py/weakscraper)
[![Build Status](https://travis-ci.org/michelbl/weakscraper.svg?branch=master)](https://travis-ci.org/michelbl/weakscraper)
[![Coverage Status](https://coveralls.io/repos/github/michelbl/weakscraper/badge.svg?branch=master)](https://coveralls.io/github/michelbl/weakscraper?branch=master)


## Description

Most HTML pages are generated using templates. Why not use templates too for scraping HTML pages? As for a template language, let's use HTML plus a few keywords. That way, the workflow with `weakscraper` is the following :
* Get the source of a HTML page you want to scrap.
* Using a few keywords, edit the HTML to select which information is of interest and which parts to discard.
* If complex processing is required, write additional callbacks in python.
* Run `weakscraper` on the template and on the HTML.


### Pros
* Observes the [rule of least power](https://en.wikipedia.org/wiki/Rule_of_least_power). A declarative language helps to focus on *what* to extract. *How* the information is scrapped is the job of the library.
* The template covers the whole page. If `weakscraper` encounters a part it is not aware of, it will throw an exception, allowing you to complete the template. There is little chance to miss information, even if a few pages contain a `div` you are not aware of at first.

### Cons
* To extract a bit of information, the whole parent list from the node root must be specified in the template. If you want to extract a few bits of information buried deep into the HTML tree, you probably want to use tools like `Beautiful Soup`.

## Install

```sh
pip install weakscraper
```

## Keywords

A `weakscraper` template is like a regular HTML file with some keywords to tell which parts are to be kept.
* `wp-name="name"` : This tag names an element in the output object. Optional if `wp-function` is set.
* `wp-recursive` : This attribute signals that everything under this tag is to be kept.
* `wp-list` : This attribute signals that this tag may be found zero, one or several time. This outputs a list.
* `wp-function="f"` : This attribute enables to process the output of the tag with a callback.
* `wp-optional` : This attribute signals that this tag can be found zero or one time.
* `wp-ignore` : As a tag, signals that everything should be ignored until the parent end tag. As an attribute, same as `wp-ignore-attrs` and `wp-ignore-content`.
* `wp-until="important-tag"` : As an attribute to the tag `wp-ignore`, signal to ignore everything until an `important-tag` is found.
* `wp-ignore-attrs` : This attribute prevents to spawn an exception if an unlisted attribute is found.
* `wp-ignore-content` : This attribute signals that the content of this tag should be ignored.
* `wp-name-attrs="name"` : This attribute that the attribute of the tag should be outputed with the name `name`. Optional if `wp-function-attrs` is set.
* `wp-function-attrs="f"` : This attribute enables to process the attributes dictionary with a callback.

## Example

`template.html`
```html
<!DOCTYPE html>
<html>
    <head>
        <title>Title</title>
    </head>
    <body attr1="val1" wp-name="body">
        <div wp-name="content"/>
    </body>
</html>
```

`webpage.html`
```html
<!DOCTYPE html>
<html>
    <head>
        <title>Title</title>
    </head>
    <body attr1="val1">
        <div>Hi !</div>
    </body>
</html>
```

`scraper.py`
```python
from weakscraper import WeakScraper


with open('template.html') as f_template, open('webpage.html') as f_html:
    template_string = f_template.read()
    html_string = f_html.read()

scraper = WeakScraper(template_string)
result_data = scraper.scrap(html_string)

with open('output.json', 'w') as f:
    f.write(json.dumps(result_data, ident=4))
```

`output.json`
```json
{
    "body": {
        "content": "Hi !"
    }
}
```

See the tests for more examples.

## How it works ?

* Class `TemplateParser` uses `html.parser` to parse the template string to a tree of dicts.
* Class `HtmlParser` uses `html.parser` to parse the HTML string to a tree of dicts.
* A tree of objects of class `Template` if recursively created from the output of a `TemplateParser`. Then it compares recursively it's own structure with the output of `HtmlParser`.
* Class `WeakScraper` glues the pieces together.

## License

MIT (http://www.opensource.org/licenses/mit-license.php)

Keywords
weakparser关键词

A weakscraper template is like a regular HTML file with some keywords to tell which parts are to be kept.
一个weakscraper模板就像一个常规的HTML文件，其中包含一些关键字来告诉哪些部分被保留。

    wp-name = "name"：
        This tag names an element in the output object. 
        该标签命名输出对象中的一个元素。
        Optional if "wp-function" is set.
        如果设置了wp-function，则可选。

    wp-recursive：
        This attribute signals that everything under this tag is to be kept.
        此属性表示要保留此标记下的所有内容。

    wp-list：
        This attribute signals that this tag may be found zero, one or several time.
        该属性表示该标签可能被发现为零次，一次或几次。
        This outputs a list.
        这将输出一个列表。

    wp-function = "f"：
        This attribute enables to process the output of the tag with a callback.
        该属性使得能够使用回调处理标签的输出。

    wp-optional：
        This attribute signals that this tag can be found zero or one time.
        该属性表示该标签可以被找到零或一次。

    wp-ignore：
        As a tag, signals that everything should be ignored until the parent end tag. 
        作为标签，表示一切都应该被忽略，直到父端标记。
        As an attribute, same as "wp-ignore-attrs" and "wp-ignore-content".
        作为属性，与wp-ignore-attrs和wp-ignore-content相同。

    wp-until =“important-tag”：
        As an attribute to the tag "wp-ignore", signal to ignore everything until an "important-tag" is found.
        作为标签wp-ignore的属性，信号忽略所有内容，直到找到一个重要的标签。

    wp-ignore-attrs：
        This attribute prevents to spawn an exception if an unlisted attribute is found.
        如果发现未列出的属性，此属性可防止产生异常。

    wp-ignore-content：
        This attribute signals that the content of this tag should be ignored.
        该属性表示该标签的内容应该被忽略。

    wp-name-attrs = "name"：
        This attribute that the attribute of the tag should be outputed with the name "name". 
        该属性应该使用名称“name”输出标签的属性。
        Optional if "wp-function-attrs" is set.
        如果设置了wp-function-attrs，则为可选项。

    wp-function-attrs = "f"：
        This attribute enables to process the attributes dictionary with a callback.
        该属性使得能够使用回调来处理属性字典。


# coding: utf-8

from naive_fsa import FiniteStateAutomata as FSA
import re

HTML_TAG_STATES = {

        "start": {
            "trans": [ ('<', 'tag_name') ]
            },

        "tag_name": {
            "trans": [ (' ', 'waiting_for_attr'), ('>', 'end') ],
            "default": "tag_name"
            },

        "waiting_for_attr": {
            "trans": [('>', 'end')],
            "default": "attr_name"
            },

        "attr_name": {
            "trans": [('=', 'attr_value_start'), ('>', 'end')],
            "default": "attr_name"
            },

        "attr_value_start": {
            "trans": [('"', 'attr_value_double_quote'), ('>', 'end')],
            "default": "attr_value_start"
            },

        "attr_value_double_quote": {
            "trans": [('"', 'end_of_attr_value')],
            "default": "attr_value_double_quote"
            },

        "attr_value_single_quote": {
            "trans": [("'", 'end_of_attr_value')],
            "default": "attr_value_single_quote"
            },

        "end_of_attr_value": { 
            "direct": "waiting_for_attr"
            },

        "end": {}

        }

HTML_FSA = FSA(HTML_TAG_STATES, start="start", end="end")

def sub_html_tag(sub, html):
    fsa = FSA(HTML_TAG_STATES, start="start", end="end")

    result, start, end = fsa.search(html)
    while result:
        html = html[:start] + str(sub) + html[end:]
        result, start, end = fsa.search(html, start)

    return html

def remove_html_tag(html):
    sub_html_tag('', html)

def clean_html(html):
    # clear new line and tab
    html = re.sub(r'[\r\n\t]', ' ', html.strip())

    # discard script tag and style tag
    html = re.sub(r'(?is)<(script|style).*?>.*?</\1>', ' ', html) 

    # discard comment
    html = re.sub(r'(?s)<!--.*?-->', ' ', html)

    # html entities replacement
    html = re.sub(r'&nbsp;', ' ', html)

    # substitute continuous blanks
    html = re.sub(r'  +', ' ', html)

    # discard html tags
    #html = re.sub(r'(?s)<.*?>', '\n', html)
    html = sub_html_tag('\n', html)
    html = re.sub(r' *\n( *\n)+', '\n', html)

    return html

if __name__ == "__main__":
    html = """
    <html>
    <head>
    <title>hello the world</title>
    <style>
    .no, p, www {
        background-color: red
    }
    </style>
    </head>
    <body>
    <p>
    para 1 hereeeeeeeeeeeeeeeeeee
    </p>
    <script type="text/javascript">
    if ( 1 < 2 && 2 > 5 ) { alert('hello world'); }
    </script>
    <p onload="if(32>1024) callfoo(); else do anit">
    para 2 whaaaaaaaaat
    </p>
    <script> <!-- 
    if (isIE) {gogogogogoogo booooooom}
    --> </script>
    <p> paragraph 333333333 </p>
    </body>
    </html>
    """
    
    fsa = FSA(HTML_TAG_STATES, start="start", end="end")

    result, start, end = fsa.search(html)
    while result:
        html = html[:start] + html[end:]
        result, start, end = fsa.search(html)

    print html


# coding: utf-8

from naive_fsa import FiniteStateAutomata as FSA

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


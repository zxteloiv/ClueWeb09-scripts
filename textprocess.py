#!/usr/bin/env python2
# coding: utf-8

import re
from bs4 import BeautifulSoup
from pycorenlp import StanfordCoreNLP

CORENLP_IP = '127.0.0.1'
CORENLP_PORT = '9000'
HTML_SAVE_PATH = './dump'

def init_CoreNLPServer():
    global CORENLP_IP
    global CORENLP_PORT
    nlpobj = StanfordCoreNLP('http://' + CORENLP_IP + ':' + CORENLP_PORT)
    return nlpobj

def preprocess(html_text):
    # discard html headers
    html_text = re.sub('^HTTP[^<]*<', '<', html_text, flags=re.DOTALL)

    # discard possible comments in raw html
    html_text = re.sub(r'<!--(.*?)-->', ' ', html_text, flags=re.DOTALL)

    # Since new line feeds in HTML have no use, 
    # remove all new lines in the original text before we do,
    # because we will use the line feed as separator for differenct sentences.
    html_text = re.sub(r'[\r\n]+', ' ', html_text)
    html_text = re.sub(r'  +', ' ', html_text)

    return html_text

def nlp_analyze(text, nlp=None):
    """Use CoreNLP to extract sentences from a paragraph."""

    # annotators must be set, otherwise the returned data will not be a struct in json.
    # Currently encoding problems reside, making the text to send not be in unicode.
    output = nlp.annotate(text.encode('utf-8'),
            properties={'annotators':'tokenize,ssplit,pos', 'outputFormat':'json'})

    # do NOT take line feed or carriage return into a sentence
    concat_token = lambda i, x: (x[u'originalText'] if i == 0
            else re.sub('\r\n|\n|\r', ' ', x[u'before']) + x[u'originalText'])

    sentences = (u''.join(concat_token(i, token) for i, token in enumerate(s[u'tokens']))
                for s in output[u'sentences'])

    for sentence in sentences:
        # preprocess rule, redundant spaces reduced to one
        sentence = re.sub(r'[\t\r\n ]+', ' ', sentence).strip()

        yield sentence

def get_sentences_from_html(html, nlp=None):
    soup = BeautifulSoup(html, 'lxml')

    # discard script and css style tag
    for tag in soup(['script', 'style']):
        tag.extract()

    # extract text from all tags.
    text = soup.get_text(separator=u'\n')

    paras = text.splitlines()

    # substitute all non-breaking space to normal space
    paras = [re.sub(u'\xa0', ' ', p) for p in paras]
    # discard comment
    paras = [p for p in paras if not (re.match(r'^[\r\n\t ]*<!--', p))]
    paras = [re.sub(r'<!--[^>]+-->', u' ', p) for p in paras]
    # substitute continuous blanks
    paras = [re.sub(r'\t+', u'\t', p) for p in paras]
    paras = [re.sub(r'[\r\n]+', u'\n', p) for p in paras]
    paras = [re.sub(r'  +', u' ', p) for p in paras]
    # discard empty string
    paras = [p.strip() for p in paras if len(p.strip()) > 0]

    # analyze sentence in a paragraph
    sentences = list(s for s in nlp_analyze("\n".join(p for p in paras), nlp))

    return sentences

def output_html(trec_id, html_data):
    global HTML_SAVE_PATH
    fout =  open('/'.join((HTML_SAVE_PATH, trec_id + ".html")), 'wb')
    fout.write(html_data)
    fout.close()

def output_sentences(trec_id, sentences):
    global HTML_SAVE_PATH
    fout = open(HTML_SAVE_PATH + '/' + trec_id + '.sentences.html', 'wb')
    fout.write('<html><head><meta charset="utf-8"><title>%s</title></head><body>' % str(trec_id))
    fout.write(u'<br/>\n------------------------------<br/>\n'.join(sentences).encode('utf-8'))
    fout.write('</body></html>')
    fout.close()


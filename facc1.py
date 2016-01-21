#!/usr/bin/env python2
# coding: utf-8

import sys

sys.path.insert(1, ("/home/zxteloiv/.local/lib/python2.7/site-packages/warc-0.2.0-py2.7.egg"))
sys.path.insert(2, ("/home/zxteloiv/local/python27/lib/python2.7/site-packages"))
sys.path.insert(3, ("/home/zxteloiv/.local/lib/python2.7/site-packages"))
sys.path.insert(4, ("/home/zxteloiv/local/python27/lib/python27.zip"))
sys.path.insert(5, ("/home/zxteloiv/local/python27/lib/python2.7"))
sys.path.insert(6, ("/home/zxteloiv/local/python27/lib/python2.7/plat-linux2"))
sys.path.insert(7, ("/home/zxteloiv/local/python27/lib/python2.7/lib-tk"))
sys.path.insert(8, ("/home/zxteloiv/local/python27/lib/python2.7/lib-old"))
sys.path.insert(9, ("/home/zxteloiv/local/python27/lib/python2.7/lib-dynload"))

import re
import warc
import reporter
from bs4 import BeautifulSoup
from pycorenlp import StanfordCoreNLP
from OrderedSet import OrderedSet

CORENLP_IP = '127.0.0.1'
CORENLP_PORT = '9000'
HTML_SAVE_PATH = './dump'

def preprocess(html_text):
    # discard html headers
    html_text = re.sub('^HTTP[^<]*(<)', r'\1', html_text, flags=re.DOTALL)

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
    soup = BeautifulSoup(html, 'html.parser')

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

def get_sentences_from_html_2(html, nlp=None):
    r = reporter.Reporter()
    r.read(html=html)
    text = r.report_news()
    sentences = list(nlp_analyze(text, nlp))
    return sentences


def process_facc1(facc1file, cluewebfile):
    global CORENLP_IP
    global CORENLP_PORT
    nlpobj = StanfordCoreNLP('http://' + CORENLP_IP + ':' + CORENLP_PORT)

    facc1 = open(facc1file, 'rb')
    clueweb = warc.open(cluewebfile, 'rb')
    record = clueweb.read_record()

    for line in facc1:
        (trec_id, encoding, entity_name, entity_start, entity_end, _, __,
                freebase_id) = line.strip().split('\t')

        #_, directory, section, record_id = trec_id.strip().split('-')

        # We can iterate over the facc1 file along the clueweb09 file, because
        # these files are all organized linearly and ordered by the WARC-TREC-ID.
        while 'warc-trec-id' not in record or record['warc-trec-id'] != trec_id:
            record = clueweb.read_record()
        else:
            html_data = preprocess(record.payload)

            sentences = get_sentences_from_html(html_data, nlpobj)
            output_html(trec_id, html_data)
            output_sentences(trec_id, sentences)

        # take the longest sentence from those the entity exists
        try:
            sentence = max((s for s in sentences if entity_name in s), key=len)
        except ValueError:
            print >> sys.stderr, line.strip()
            continue

        print "\t".join(x for x in (
            trec_id, entity_name, freebase_id, re.sub(r'\t', u' ', sentence).encode('utf-8')
            ))

    facc1.close()
    clueweb.close()

def output_html(trec_id, html_data):
    global HTML_SAVE_PATH
    fout =  open('/'.join((HTML_SAVE_PATH, trec_id + ".html")), 'wb')
    fout.write(html_data)
    fout.close()

def output_sentences(trec_id, sentences):
    global HTML_SAVE_PATH
    fout = open(HTML_SAVE_PATH + '/' + trec_id + '.sentences.txt', 'wb')
    fout.write(u'<br/>\n------------------------------<br/>\n'.join(sentences).encode('utf-8'))
    fout.close()

if __name__ == "__main__":
    if len(sys.argv) == 3:
        process_facc1(sys.argv[1], sys.argv[2])
    else:
        print "Usage: %s <facc1 file> <annote file>" % sys.argv[0]
    pass


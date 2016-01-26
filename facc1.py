#!/usr/bin/env python2
# coding: utf-8

import sys

sys.path.insert(1, ("./warc-clueweb"))

import re
import warc
import textprocess as tp

def process_facc1_with_filename(facc1file, cluewebfile):
    facc1_obj = open(facc1file, 'rb')
    clueweb_obj = warc.open(cluewebfile, 'rb')

    process_facc1_with_fileobj(facc1_obj, clueweb_obj)

    facc1_obj.close()
    clueweb_obj.close()

def process_facc1_with_fileobj(facc1_obj, clueweb_obj, logout=sys.stdout, logerr=sys.stderr):
    nlpobj = tp.init_CoreNLPServer()
    record = clueweb_obj.read_record()

    for line in facc1_obj:
        (trec_id, encoding, entity_name, entity_start, entity_end, _, __,
                freebase_id) = line.strip().split('\t')

        #_, directory, section, record_id = trec_id.strip().split('-')

        # We can iterate over the facc1 file along the clueweb09 file, because
        # these files are all organized linearly and ordered by the WARC-TREC-ID.
        while 'warc-trec-id' not in record or record['warc-trec-id'] != trec_id:
            record = clueweb_obj.read_record()
        else:
            try:
                html_data = tp.preprocess(record.payload)

                sentences = tp.get_sentences_from_html(html_data, nlpobj)
                #tp.output_html(trec_id, html_data)
                #tp.output_sentences(trec_id, sentences)
            except:
                logerr.write("\t".join((line.strip(), re.sub(r'\r\n', '', html_data))) + "\n")
                continue

        # take the longest sentence from those the entity exists
        try:
            sentence = max((s for s in sentences if entity_name in s), key=len)
        except ValueError:
            logerr.write(line.strip() + "\n")
            continue

        logout.write("\t".join(x for x in (
            trec_id, entity_name, freebase_id, re.sub(r'\t', u' ', sentence).encode('utf-8')
            )) + "\n")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        process_facc1_with_filename(sys.argv[1], sys.argv[2])
    else:
        print "Usage: %s <facc1 file> <annote file>" % sys.argv[0]


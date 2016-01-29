#!/usr/bin/env python2
# coding: utf-8

import sys

sys.path.insert(1, ("./py-corenlp"))
sys.path.insert(1, ("./warc-clueweb"))
sys.path.insert(1, ("./requests"))

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
    entity_set = set()
    is_a_new_record = True

    for line in facc1_obj:
        (trec_id, encoding, entity_name, entity_start, entity_end, _, __,
                freebase_id) = line.strip().split('\t')

        # We can iterate over the facc1 file along the clueweb09 file, because
        # these files are all organized linearly and ordered by the WARC-TREC-ID.
        while record is not None and 'warc-trec-id' not in record or record['warc-trec-id'] != trec_id:
            record = clueweb_obj.read_record()
            is_a_new_record = True
            sentences = []

        if record is None:
            break

        try:
            if is_a_new_record:
                is_a_new_record = False
                html_data = tp.preprocess(record.payload)

                # each time a new html file is parsed, a new entity_set must be presented.
                entity_set.clear()

                #logerr.flush()
                #logout.flush()

                sentences = tp.get_sentences_from_html_v2(html_data, nlpobj)
                #tp.output_html(trec_id, html_data)
                #tp.output_sentences(trec_id, sentences)
        except:
            logerr.write("\t".join((line.strip(), "failed_to_get_sentences", re.sub(r'\r\n', '', html_data))) + "\n")
            continue

        if freebase_id in entity_set:
            continue
        else:
            entity_set.add(freebase_id)

        # take the longest sentence from those the entity exists
        try:
            sentence = max((s for s in sentences if entity_name in s), key=len)
        except ValueError:
            logerr.write(line.strip() + "\tentity_not_found\n")
            continue

        logout.write("\t".join(x for x in (
            trec_id, entity_name, freebase_id, re.sub(r'\t', u' ', sentence).encode('utf-8')
            )) + "\n")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        process_facc1_with_filename(sys.argv[1], sys.argv[2])
    else:
        print "Usage: %s <facc1 file> <clueweb file>" % sys.argv[0]


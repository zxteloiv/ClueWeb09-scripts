#!/usr/bin/env python2
# coding: utf-8

import sys, os

for lib in os.listdir('./lib'):
    sys.path.insert(1, './lib/' + lib)

import re
import warc
import textprocess as tp
import xuxian

parser = xuxian.get_parser()
parser.add_argument('--facc1-file', required=True)
parser.add_argument('--clueweb-file', required=True)
parser.add_argument('--output-file', required=True)
parser.add_argument('--error-file', required=True)
parser.add_argument('--task-id', required=True)

def process_facc1_with_filename(args):
    facc1_obj = open(args.facc1_file, 'rb')
    clueweb_obj = warc.open(args.clueweb_file, 'rb')

    process_facc1_with_fileobj(facc1_obj, clueweb_obj)

    facc1_obj.close()
    clueweb_obj.close()

def process_facc1_with_fileobj(facc1_obj, clueweb_obj):
    nlpobj = tp.init_CoreNLPServer()
    record = clueweb_obj.read_record()
    entity_set = set()
    is_a_new_record = True

    args = xuxian.get_args()
    logout = xuxian.apply_dump_file('output', args.output_file)
    logerr = xuxian.apply_dump_file('error', args.error_file)

    recovery_state = xuxian.recall(args.task_id)

    for line in facc1_obj:
        (trec_id, encoding, entity_name, entity_start, entity_end, _, __,
                freebase_id) = line.strip().split('\t')

        # We can iterate over the facc1 file along the clueweb09 file, because
        # these files are all organized linearly and ordered by the WARC-TREC-ID.
        while record is not None and 'warc-trec-id' not in record or record['warc-trec-id'] != trec_id:
            record = clueweb_obj.read_record()
            is_a_new_record = True
            sentences = []

            if recovery_state == trec_id:
                recovery_state = None

        if record is None:
            break

        if recovery_state is not None:
            continue

        if is_a_new_record:
            try:
                html_data = tp.preprocess(record.payload)
                # each time a new html file is parsed, a new entity_set must be presented.
                entity_set.clear()
                sentences = tp.get_sentences_from_html_v2(html_data, nlpobj)
                is_a_new_record = False
            except:
                logerr.info("\t".join((line.strip(), "failed_to_get_sentences", re.sub(r'\r\n', '', html_data))) + "\n")
                continue

        if freebase_id in entity_set:
            continue
        else:
            entity_set.add(freebase_id)

        # take the longest sentence from those the entity exists
        try:
            sentence = max((s for s in sentences if entity_name in s), key=len)
        except ValueError:
            logerr.info(line.strip() + "\tentity_not_found\n")
            continue

        logout.info("\t".join(x for x in (
            trec_id, entity_name, freebase_id, re.sub(r'\t', u' ', sentence).encode('utf-8')
            )) + "\n")

if __name__ == "__main__":
    xuxian.parse_args()
    xuxian.run(process_facc1_with_filename)


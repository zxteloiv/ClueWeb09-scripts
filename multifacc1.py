#!/usr/bin/env python2
# coding: utf-8

import sys

sys.path.insert(1, ("./warc-clueweb"))

import re
import multiprocessing
import tarfile

import facc1
import warc

LOGGER_PATH='./dump'

def worker(pid, pnum, facc1tgz, clueweb_path):
    tar = tarfile.open(facc1tgz, 'r:gz')

    for (i, member) in enumerate(tar):
        if i % pnum != pid or not member.isfile():
            continue

        # member name is like "ClueWeb09_English_1/en0000/00.anns.tsv"
        dirname, section, record = member.name.split('/')
        filename = record.split('.')[0]

        clueweb_filename = '/'.join((clueweb_path, dirname, section, filename)) + '.warc.gz'
        clueweb_obj = warc.open(clueweb_filename, 'rb')

        facc1_obj = tar.extractfile(member)

        uniqkey = '-'.join((section, filename, 'entity-sentence'))
        logout = open(LOGGER_PATH + '/' + uniqkey + '.out', 'wb')
        logerr = open(LOGGER_PATH + '/' + uniqkey + '.err', 'wb')

        facc1.process_facc1_with_fileobj(facc1_obj, clueweb_obj, logout=logout, logerr=logerr)

        logout.close()
        logerr.close()

def multifacc1(facc1tgz, clueweb_path):
    PROCESS_NUM = 16
    process_list = [multiprocessing.Process(target=worker, args=(i, PROCESS_NUM, facc1tgz, clueweb_path))
            for i in xrange(PROCESS_NUM)]

    for process in process_list:
        process.start()

    for process in process_list:
        process.join()

if __name__ == "__main__":
    if len(sys.argv) == 3:
        multifacc1(sys.argv[1], sys.argv[2])
        

#!/bin/bash

[ -d dump ] && rm -r dump
mkdir -p dump/state

python facc1.py \
    --facc1-file=FACC1/profile.ids.tmp \
    --clueweb-file=/media/ClueWeb09/ClueWeb09_English_1/en0000/00.warc.gz \
    --output-file=dump/all.out \
    --error-file=dump/all.err \
    --sys-log-path=dump \
    --state-path=dump/state \
    --task-id=temptask

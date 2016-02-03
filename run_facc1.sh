
mkdir -p dump
rm dump/*

# python facc1.py --facc1-file=FACC1/profile.ids.tmp --clueweb-file=/media/ClueWeb09/ClueWeb09_English_1/en0000/00.warc.gz --output-file=dump/all.out --error-file=dump/all.err --sys-log-path=
python facc1.py \
    --facc1-file=FACC1/profile.ids.tmp \
    --clueweb-file=/media/ClueWeb09/ClueWeb09_English_1/en0000/00.warc.gz \
    --output-file=dump/all.out \
    --error-file=dump/all.err \
    --sys-log-path=dump

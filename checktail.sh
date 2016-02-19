#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 dirname(en0041) fileid(13) [opt]"
    echo "	by default opt will be 'eosa'"
    echo "	e: error, o: out, s: state, a: annsfile"
    exit;
fi

dirnum=$1
fileid=$2

opt=$3

if [ ! -n $opt ]; then
    opt="eosa"
fi

case "$opt" in
    *e*)
        echo "err===>"
        tail -5 dump/${dirnum}_${fileid}.err 
        ;;
esac

case "$opt" in
    *o*)
        echo ""
        echo "out===>"
        tail -5 dump/${dirnum}_${fileid}.out 
        ;;
esac

case "$opt" in
    *s*)
        echo ""
        echo "state===>"
        tail -5 dump/state/${dirnum}_${fileid}
        echo ""
        ;;
esac

case "$opt" in
    *a*)
        echo ""
        echo "anns.tsv===>"
        tail -5 ~/data/FACC1/ClueWeb09_English_4/${dirnum}/${fileid}.anns.tsv 
        ;;
esac

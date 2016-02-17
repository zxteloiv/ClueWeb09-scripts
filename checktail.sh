#!/bin/bash

dirnum=$1
fileid=$2

echo "err===>"
tail -5 dump/${dirnum}_${fileid}.err 

echo ""
echo "out===>"
tail -5 dump/${dirnum}_${fileid}.out 

echo ""
echo "state===>"
tail -5 dump/state/${dirnum}_${fileid}
echo ""

echo ""
echo "anns.tsv===>"
tail -5 ~/data/FACC1/ClueWeb09_English_4/${dirnum}/${fileid}.anns.tsv 

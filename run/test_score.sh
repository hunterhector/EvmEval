#!/bin/sh 
system=$1
echo "Scoring $1 against gold"
../scorer.py  -g ../data/converted/test.gold.tbf -s ../data/converted/test.$1.tbf -p ../data/tkn/test_tokens/ -d test.$1.comp -o test.$1.eval

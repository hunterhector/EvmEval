#!/bin/sh 
echo '\nConverting text from brat to TBF format'
# an extension will be automatically added to the end of the file
./brat2tokenFormat.py -t LDC2014R55_LDC_tokenized/token-maps/ -d LDC2014R55_LDC_tokenized/ann -o LDC2014R55_LDC_tokenized/output/LDC2014R55_LDC_gold -te .txt.tab -oe .tkn.ann -w
echo '\nEvaluating the system on itself, which means a perfect system'
./scorer.py -t LDC2014R55_LDC_tokenized/token-maps/ -g LDC2014R55_LDC_tokenized/output/LDC2014R55_LDC_gold.tbf -s LDC2014R55_LDC_tokenized/output/LDC2014R55_LDC_gold.tbf -d LDC2014R55_LDC_tokenized/output/LDC2014R55_LDC_comp -o LDC2014R55_LDC_tokenized/output/LDC2014R55_score -w

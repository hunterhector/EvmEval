#!/bin/sh 
echo '\nConverting text from brat to TBF format'
# an extension will be automatically added to the end of the file
./brat2tokenFormat.py -t data/private/R55/token_map/ -d data/private/R55/ann -o data/private/R55/output/LDC2014R55_LDC_gold -te .txt.tab.cut -oe .tbf -ae .tkn.ann -w -b
echo '\nEvaluating the system on itself, which means a perfect system'
./scorer.py -t data/private/R55/token-maps/ -g data/private/R55/output/LDC2014R55_LDC_gold.tbf -s data/private/R55/output/LDC2014R55_LDC_gold.tbf -d data/private/R55/output/LDC2014R55_LDC_comp -o data/private/R55/output/LDC2014R55_score -w

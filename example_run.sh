#!/bin/sh 

echo "\nConverting text from brat to TBF format"
./brat2tokenFormat.py -t example_data/tkn/ -d example_data/ann -o example_data/example -w
echo "\nEvaluating system A, should be a perfect system\n"
./scorer.py -s example_data/ -g example_data/example.tbf -s example_data/sample_system_A.tbf -d example_data/A_out -t example_data/tkn/ -w 
echo "\nEvaluating system B, with one token missed\n"
./scorer.py -s example_data/ -g example_data/example.tbf -s example_data/sample_system_B.tbf -d example_data/B_out -t example_data/tkn/ -w

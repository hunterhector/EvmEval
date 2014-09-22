#!/bin/sh 

echo "Tokenizing plain text\n"
java -jar evm-eval-1.0.2-jar-with-dependencies.jar -a example_data/ann/ -e txt -o example_data/tkn/ -t example_data/txt/ 
echo "\nConverting text from brat to TBF format"
./brat2tokenFormat.py -t example_data/tkn/ -d example_data/ann -o example_data/example -w
echo "\nEvaluating system A, should be a perfect system\n"
./scorer.py -s example_data/ -g example_data/example.tbf -s example_data/sample_system_A.tbf -d example_data/A_out -t example_data/tkn/ -w 
echo "\nEvaluating system B, with one token missed\n"
./scorer.py -s example_data/ -g example_data/example.tbf -s example_data/sample_system_B.tbf -d example_data/B_out -t example_data/tkn/ -w

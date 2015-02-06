#!/bin/sh 

echo "Converting text from brat to TBF format\n"
./brat2tokenFormat.py -t example_data/tkn/ -d example_data/ann -o example_data/gold -w -b -ae .tkn.ann -te .txt.tab
echo "Evaluating system A, should be a perfect system\n"
./scorer_v1.1.py -g example_data/gold.tbf -s example_data/sample_system_A.tbf -d example_data/A_out -t example_data/tkn/ -o example_data/perfect_score -w -b -te .txt.tab
echo "Stored score report at example_data/prefect_score\n"
echo "Evaluating system B, with one token missed\n"
./scorer_v1.1.py -g example_data/gold.tbf -s example_data/sample_system_B.tbf -d example_data/B_out -t example_data/tkn/ -o example_data/one_miss_score -w -b -te .txt.tab
echo "Stored score report at example_data/one_miss_score"

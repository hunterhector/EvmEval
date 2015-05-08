#!/bin/sh 

echo "Converting text from brat to TBF format\n"
./brat2tbf.py -t data/example_data/tkn/ -d data/example_data/ann -o data/example_data/gold -b -ae .tkn.ann -te .txt.tab -w
echo "Evaluating system A, should be a perfect system\n"
./scorer_v1.3.py -g data/example_data/gold.tbf -s data/example_data/sample_system_A.tbf -d data/example_data/A_out.tmp -t data/example_data/tkn/ -o data/example_data/perfect_score.tmp -b
echo "Stored score report at data/example_data/prefect_score.tmp\n"
echo "Evaluating system B, with one file missed\n"
./scorer_v1.3.py -g data/example_data/gold.tbf -s data/example_data/sample_system_B.tbf -d data/example_data/B_out.tmp -t data/example_data/tkn/ -o data/example_data/one_miss_score.tmp -b
echo "Stored score report at data/example_data/one_miss_score.tmp"

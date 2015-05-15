#!/bin/sh 

echo "Evaluating system A, should be a perfect system\n"
./scorer_v1.3.py -g data/scoring_demo/gold.tbf -s data/scoring_demo/sample_system_A.tbf -d data/scoring_demo/A_out.tmp -t data/scoring_demo/tkn/ -o data/scoring_demo/perfect_score.tmp -b
echo "Stored score report at data/scoring_demo/prefect_score.tmp\n"
echo "Evaluating system B, with one file missed\n"
./scorer_v1.3.py -g data/scoring_demo/gold.tbf -s data/scoring_demo/sample_system_B.tbf -d data/scoring_demo/B_out.tmp -t data/scoring_demo/tkn/ -o data/scoring_demo/one_miss_score.tmp -b
echo "Stored score report at data/scoring_demo/one_miss_score.tmp"
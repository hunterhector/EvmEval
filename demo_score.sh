#!/bin/sh 
scorer=./scorer_v1.8.py

char_dir=data/scoring_demo/char_based
token_dir=data/scoring_demo/token_based

echo "==== Demo of token based scoring ====\n"

echo "Evaluating system A, should be a perfect system\n"
$scorer -g $token_dir/gold.tbf -s $token_dir/sample_system_A.tbf -d $token_dir/A_out.tmp -t $token_dir/tkn/ -o $token_dir/score_prefect.scores
echo "Stored score report at $token_dir/score_prefect.scores\n"

echo "Evaluating system B, with one file missed\n"
$scorer -g $token_dir/gold.tbf -s $token_dir/sample_system_B.tbf -d $token_dir/B_out.tmp -t $token_dir/tkn/ -o $token_dir/score_miss_one_file.scores
echo "Stored score report at $token_dir/score_miss_one_file.scores"

echo "Evaluating system C, with some token and type errors\n"
$scorer -g $token_dir/gold.tbf -s $token_dir/sample_system_C.tbf -d $token_dir/C_out.tmp -t $token_dir/tkn/ -o $token_dir/score_system_C.scores
echo "Stored score report at $token_dir/score_system_C.scores"

echo "Evaluating system D, with no response\n"
$scorer -g $token_dir/gold.tbf -s $token_dir/sample_system_D.tbf -d $token_dir/D_out.tmp -t $token_dir/tkn/ -o $token_dir/score_empty.scores
echo "Stored score report at $token_dir/score_empty.scores"


echo "\n==== Demo of character based scoring ====\n"
echo "Evaluating system A (character based), should be a perfect system\n"
$scorer -g $char_dir/gold.tbf -s $char_dir/system_A.tbf -d $char_dir/A_out.tmp -o $char_dir/score_prefect.scores
echo "Stored score report at $char_dir/score_prefect.scores\n"


echo "\n==== Demo of temporal scoring ====\n"
echo "Evaluating a temporal sample (character based)\n"
$scorer -g $char_dir/gold.tbf -s $char_dir/temporal_sample.tbf -d $char_dir/A_out.tmp -a $char_dir/temporal_output -o $char_dir/score_temporal.scores 
echo "Stored score report at $char_dir/score_temporal.scores\n"

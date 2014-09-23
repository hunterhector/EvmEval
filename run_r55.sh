#!/bin/sh 
#example arguments : 19 ERE sue
./scorer.py -t data/R55_test_data/token-maps/ -g output/tbf/LDC2014R"$1"_"$2"_gold.tbf -s output/tbf/LDC2014R"$1"_"$2"_"$3".tbf -d output/comp/LDC2014R"$1"_"$2"_"$3" -o output/scores/LDC2014R"$1"_"$2"_"$3" -w

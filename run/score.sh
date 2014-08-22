#!/bin/sh 
../scorer.py  -g ../data/converted/example.gold.tbf -s ../data/converted/example.system.tbf -t ../data/tkn/LDC2014R19/ -d ../sample_score/example.comp -o ../sample_score/example.eval -w
../scorer.py -g ../data/converted/gold.tbf -s ../data/converted/yukari.tbf -t ../data/tkn/LDC2014R19/ -o ../sample_score/yukari.scores -d ../sample_score/yukari.compare.tbf -w
../scorer.py -g ../data/converted/gold.tbf -s ../data/converted/sue.tbf -t ../data/tkn/LDC2014R19/ -o ../sample_score/sue.scores -d ../sample_score/sue.compare.tbf -w 

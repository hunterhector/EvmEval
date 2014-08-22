#!/bin/sh 
../scorer.py  -g ../data/converted/example.gold.tbf -s ../data/converted/example.system.tbf -p ../data/tkn/LDC2014R19/ -d ../sample_score/example.comp -o ../sample_score/example.eval
../scorer.py -g ../data/converted/gold.tbf -s ../data/converted/yukari.tbf -p ../data/tkn/LDC2014R19/ -o ../sample_score/yukari.scores -d ../sample_score/yukari.compare.tbf
../scorer.py -g ../data/converted/gold.tbf -s ../data/converted/sue.tbf -p ../data/tkn/LDC2014R19/ -o ../sample_score/sue.scores -d ../sample_score/sue.compare.tbf 

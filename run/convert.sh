#!/bin/sh 
../brat2tokenFormat.py -d ../data/ann/gold/ -o ../data/converted/gold -i gold -t ../data/tkn/LDC2014R19/
../brat2tokenFormat.py -d ../data/ann/sue/ -o ../data/converted/sue -i sue -t ../data/tkn/LDC2014R19/
../brat2tokenFormat.py -d ../data/ann/yukari/ -o ../data/converted/yukari -i yukari -t ../data/tkn/LDC2014R19/

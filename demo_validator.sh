#!/bin/sh 
for file in data/test_cases/wrong_format_tests/*.tbf
do
	./validator.py -s $file -t data/test_cases/wrong_format_tests/tkn
	echo "Error code for file "$file" is "$?
done

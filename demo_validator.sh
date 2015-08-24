#!/bin/sh 
for file in data/test_cases/wrong_format_tests/*.tbf
do
	./validator.py -t data/test_cases/wrong_format_tests/tkn -s $file
	echo "Error code for file "$file" is "$?
done

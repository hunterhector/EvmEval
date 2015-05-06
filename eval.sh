#!/bin/sh 
ANNOTATION_DATA_PATH=data/private/pilot_submissions/LDC2015R04_DEFT_2014_Event_Nugget_Evaluation_Annotation_Data/
SUBMISSION_DATA_PATH=data/private/pilot_submissions/all_submission
TOKEN_MAP_PATH=$ANNOTATION_DATA_PATH"data/token_offset"
GOLD_STANDARD_PATH=$ANNOTATION_DATA_PATH"annotation.tbf"
RESULT_PATH=data/private/pilot_submissions/results_1.2/

for submission in $SUBMISSION_DATA_PATH/*
do
	basename=${submission##*/}
	echo "Processing $basename"
	./scorer_v1.2.py -g $GOLD_STANDARD_PATH -s $submission -o $RESULT_PATH$basename".results" -t $TOKEN_MAP_PATH
done


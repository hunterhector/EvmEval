#!/bin/sh 

# This script run multiple submissions, and save the scoring results.
if [ $# -ne 4 ]; then
	echo "Usage: $0 [The gold standard file] [The submission data] [Directory for result] [The language sub directory]"
	exit 1
fi

# The unpacked directories that contains the gold standard and submission runs. 
nugget_gold_tbf=$1
submission_dir=$2
base_result_dir=$3
language=$4

nugget_sub_dir="event-nugget-splitted/"${language}
coref_sub_dir="event-coref-splitted/"${language}

scorer=./scorer_v1.8.py

echo ${submission_dir}"/"${nugget_sub_dir}
find ${submission_dir}"/"${nugget_sub_dir} ! -path ${submission_dir}"/"${nugget_sub_dir} -type d

# Eval nugget.
nugget_dir=${submission_dir}"/"${nugget_sub_dir}
for f in `find ${submission_dir}"/"${nugget_sub_dir} ! -path ${submission_dir}"/"${nugget_sub_dir} -type f`
do
	sys_name=${f##*/}
	sys_file=${f}
	result_dir=${base_result_dir}"/nugget/"${language}"/"${sys_name}
	echo "Evaluating "${sys_file}" for nugget detection, writing results to "${result_dir}
	${scorer} -g ${nugget_gold_tbf} -s ${sys_file} -o ${result_dir}"/eval.scores" -d ${result_dir}"/gold_sys_diff"
done

: <<'END'

coref_dir=${submission_dir}"/"${coref_sub_dir}
for f in `find ${coref_dir} ! -path ${coref_dir} -type f`
do
	sys_name=${f##*/}
	sys_file=${f}
	result_dir=${base_result_dir}"/coreference/"${language}"/"${sys_name}
	echo "Evaluating "${sys_file}" for nugget coreference, writing results to "${result_dir}
	${scorer} -g ${nugget_gold_tbf} -s ${sys_file} -o ${result_dir}"/eval.scores" -d ${result_dir}"/gold_sys_diff" -c ${result_dir}"/coref.out"
done

END

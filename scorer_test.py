#!/usr/bin/python

"""
    Run the scorer through test cases

    This run the scorer in an external way and go through the scores in file to determine the correctness. Though
    calling the functions and checking the return values might be a better way, a standalone tester like this is easier
"""
import subprocess
import os

scorer_executable = "scorer_v1.5.py"
test_temp = "test_tmp"

def run_scorer(gold_path, system_path, token_path, result_out, coref_log):
    """
        Run the scorer script and provide arguments for output
    :param gold_path: The path to the gold standard file
    :param system_path: The path to the system file
    :param result_out: Path to output the scores
    :return:
    """
    with open(result_out, 'wb', 0) as out_file:
        subprocess.call(
            ["python", scorer_executable, '-g', gold_path, '-s', system_path, '-t', token_path, '-c', coref_log],
            stdout=out_file)

def extract_key_metrics(result_out, coref_log):
    pass

def run_test(test_dir):
    """
    Go through test cases in the directory, run and compare against the expected scores
    :param test_dir:
    :return:
    """
    pass

if not os.path.exists(test_temp):
    os.mkdir(test_temp)
run_scorer("data/scoring_demo/gold.tbf", "data/scoring_demo/sample_system_A.tbf", "data/scoring_demo/tkn",
           test_temp + os.sep + "score.tmp", test_temp + os.sep + "coref.temp")

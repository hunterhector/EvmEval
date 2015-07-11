#!/usr/bin/python

"""
    Run the scorer through test cases

    This run the scorer in an external way and go through the scores in file to determine the correctness. Though
    calling the functions and checking the return values might be a better way, a standalone tester like this is easier
"""
import subprocess
import os
import glob
import logging


class Config:
    """
    Configuration variables
    """
    scorer_executable = "scorer_v1.5.py"
    test_temp = "test_tmp"
    test_log_output = "test.log"
    detection_test_cases = test_temp + os.pathsep + "mention_detection_test"
    conll_test_cases = test_temp + os.pathsep + "conll_test"
    wrong_format_test_cases = test_temp + os.pathsep + "wrong_format"


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
            ["python", Config.scorer_executable, '-g', gold_path, '-s', system_path, '-t', token_path, '-c', coref_log],
            stdout=out_file)


def extract_key_metrics(result_out, coref_log):
    pass


class ScorerTest:
    def __init__(self, config):
        self.config = config
        # Prepare test temporary output.
        if not os.path.exists(config.test_temp):
            os.mkdir(config.test_temp)
        self.logger = logging.getLogger()
        test_result_output = open(self.gen_temp_file_name(Config.test_log_output), 'w')
        stream_handler = logging.StreamHandler(test_result_output)
        stream_handler.setFormatter(logging.Formatter('[%(levelname)s] %(asctime)s : %(message)s'))
        self.logger.addHandler(stream_handler)
        self.num_tests_finished = 0
        self.num_tests_passed = 0

    def gen_temp_file_name(self, temp_file_name):
        return self.config.test_temp + os.sep + temp_file_name

    def run_mention_detection_tests(self, mention_test_dir):
        pass

    def run_conll_tests(self, conll_test_dir):
        pass

    def record_pass(self):
        self.num_tests_finished += 1
        self.num_tests_passed += 1

    def record_fail(self):
        self.num_tests_finished += 1

    def run_format_error_tests(self, wrong_format_test_dir):
        """
        Run through the test cases that should make scorer raise format exceptions.
        Tests are passed
        :param wrong_format_test_dir:
        :return:
        """
        self.logger.info("Running format error test cases.")
        reference_gold = wrong_format_test_dir + os.pathsep + "correct_example.tbf"
        for f in glob.glob(wrong_format_test_dir + os.pathsep + "*.tbf"):
            if f != reference_gold:
                run_scorer(reference_gold, f, "data/scoring_demo/tkn",
                           self.config.test_temp + os.sep + "score.tmp", self.gen_temp_file_name("error_test"))
                self.record_pass()

    def run_all(self):
        self.logger.info("Start tests.")

        self.run_mention_detection_tests(Config.detection_test_cases)
        self.run_format_error_tests(Config.wrong_format_test_cases)
        self.run_conll_tests(Config.conll_test_cases)

        self.logger.info("All test finished.")
        self.logger.info("Number of tests : %d, number of tests passed : %d, number of tests failed : %d",
                         self.num_tests_finished, self.num_tests_passed,
                         self.num_tests_finished - self.num_tests_passed)


def main():
    test = ScorerTest(Config())
    test.run_all()


if __name__ == "__main__":
    main()

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
    test_base = "data/test_cases"
    test_log_output = "test.log"
    detection_test_cases = test_base + os.path.sep + "mention_detection_tests"
    conll_test_cases = test_base + os.path.sep + "conll_tests"
    wrong_format_test_cases = test_base + os.path.sep + "wrong_format_tests"
    test_file_suffix = ".tbf"
    format_test_suffix = ".reason"


def run_scorer(gold_path, system_path, token_path, result_out, coref_log):
    """
        Run the scorer script and provide arguments for output
    :param gold_path: The path to the gold standard file
    :param system_path: The path to the system file
    :param result_out: Path to output the scores
    :return:
    """
    cmd = ["python", Config.scorer_executable, '-g', gold_path, '-s', system_path, '-t', token_path, '-c',
           coref_log]

    with open(result_out, 'wb', 0) as out_file:
        subprocess.call(cmd, stdout=out_file)
    return " ".join(cmd)


def extract_key_metrics(result_out, coref_log):
    pass


class ScorerTest:
    def __init__(self, config):
        self.config = config
        # Prepare test temporary output.
        if not os.path.exists(config.test_temp):
            os.mkdir(config.test_temp)
        self.logger = logging.getLogger()
        test_out = self.gen_temp_file_name(Config.test_log_output)
        test_result_output = open(test_out, 'w')
        stream_handler = logging.StreamHandler(test_result_output)
        stream_handler.setFormatter(logging.Formatter('[%(levelname)s] %(asctime)s : %(message)s'))
        self.logger.addHandler(stream_handler)
        self.logger.setLevel(logging.INFO)
        self.num_tests_finished = 0
        self.num_tests_passed = 0

        print "Please see %s for test logs." % test_out

    @staticmethod
    def check_reason_file(output_path, reason_path):
        with open(output_path, 'r', 0) as f:
            file_str = f.read()
            reason = open(reason_path).read().strip()
            if reason in file_str:
                return True

    def gen_temp_file_name(self, temp_file_name):
        return self.config.test_temp + os.sep + temp_file_name

    def run_mention_detection_tests(self, mention_test_dir):
        pass

    def run_conll_tests(self, conll_test_dir):
        pass

    def record_pass(self):
        self.num_tests_finished += 1
        self.num_tests_passed += 1

    def record_fail(self, msg):
        self.num_tests_finished += 1
        self.logger.error("Test Failed : %s" % msg)

    def run_format_error_tests(self, wrong_format_test_dir):
        """
        Run through the test cases that should make scorer raise format exceptions,
        and that there are relevant error message in the output.
        :param wrong_format_test_dir:
        :return:
        """
        self.logger.info("Running format error test cases.")
        reference_gold = wrong_format_test_dir + os.path.sep + "correct_example.tbf"
        token_path = wrong_format_test_dir + os.path.sep + "tkn"

        self.logger.info(wrong_format_test_dir + os.path.sep + "*" + Config.test_file_suffix)

        for f in glob.glob(wrong_format_test_dir + os.path.sep + "*" + Config.test_file_suffix):
            if f != reference_gold:
                basename = os.path.basename(f)[:-len(Config.test_file_suffix)]
                scoring_out = self.config.test_temp + os.sep + basename + ".score_tmp"
                conll_out = self.gen_temp_file_name(basename + ".conll_log")

                # Reason file stores the reason why this tbf is wrong, must be matched to pass this test.
                reason_file = wrong_format_test_dir + os.sep + basename + Config.format_test_suffix
                command_run = run_scorer(reference_gold, f, token_path, scoring_out, conll_out)
                self.logger.info("Test command is  : %s" % command_run)

                if self.check_reason_file(scoring_out, reason_file):
                    self.record_pass()
                else:
                    self.record_fail("Test [%s] is not passed, reasons not found in output.")

    def run_all(self):
        self.logger.info("Start tests.")
        self.run_mention_detection_tests(Config.detection_test_cases)
        self.run_format_error_tests(Config.wrong_format_test_cases)
        self.run_conll_tests(Config.conll_test_cases)
        test_finish = self.test_finish_info()
        self.logger.info(test_finish)
        print test_finish

    def test_finish_info(self):
        return "All test finished.\nNumber of tests : %d, number of tests passed : %d, number of tests failed : %d\n" % (
            self.num_tests_finished, self.num_tests_passed,
            self.num_tests_finished - self.num_tests_passed)


def main():
    test = ScorerTest(Config())
    test.run_all()


if __name__ == "__main__":
    main()

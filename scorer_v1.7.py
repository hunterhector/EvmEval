#!/usr/bin/python

"""
    A simple scorer that reads the CMU Event Mention Format (tbf)
    data and produce a mention based F-Scores.

    It could also call the CoNLL coreference implementation and
    produce coreference results.

    This scorer also require token files to conduct evaluation.

    Author: Zhengzhong Liu ( liu@cs.cmu.edu )
"""
# Change log v1.7.0
# 1. Changing the way of mention mapping to coreference, so that it will not favor too much on recall.
# 2. Speed up on the coreference scoring since we don't need to select the best, we can convert in one single step.
# 3. Removing "what" from invisible list.
# 4. Small changes on the way of looking for the scorer.

# Change log v1.6.2:
# 1. Add clusters in the comparison output. No substantial changes in scoring.

# Change log v1.6.1:
# 1. Minor change that remove punctuation and whitespace in attribute types and lowercase all types to make system
# output more flexible.

# Change log v1.6:
# 1. Because there are too many double annotation, now such ambiguity are resolved arbitrarily:
#    a. For mention scoring, the system mention is mapped to a gold mention greedily.
#    b. The coreference evaluation relies on the mapping produced by mention mapping at mention type level. This means
#        that a system mention can only be mapped to a gold mention when their mention type matches.

# Change log v1.5:
# 1. Given that the CoNLL scorer only score exact matched mentions, we convert input format.
#    to a simplified form. We produce a mention mappings and feed to the scorer.
#    In case of double tagging, there are multiple way of mention mappings, we will produce all
#    possible ways, and use the highest final score mapping.
# 2. Fix a bug that crashes when generating text output from empty responses.
# 3. Write out the coreference scores into the score output.
# 4. Move global variables into class wrappers.
# 5. Current issue: gold standard coreference cannot be empty! Maybe file a bug to them.

# Change log v1.4:
# 1. Global mention span check: do not allow duplicate mention span with same type.
# 2. Within cluster mention span check : do not allow duplicate span in one cluster.

# Change log v1.3:
# 1. Add ability to convert input format to conll format, and feed it to the coreference resolver.
# 2. Clean up and remove global variables.

# Change log v1.2:
# 1. Change attribute scoring, combine it with mention span scoring.
# 2. Precision for span is divided by #SYS instead of TP + FP.
# 3. Plain text summary is made better.
# 4. Separate the visualization code out into anther file.

# Change log v1.1:
# 1. If system produce no mentions, the scorer should penalize it instead of ignore it.
# 2. Enhance the output of the comparison file, add the system actual output side by side for easy debug.
# 3. Add the ability to compare system and gold mentions using Brat embedded visualization.
# 4. For realis type not annotated, give full credit as long as system give a result.
# 5. Add more informative error message.

import argparse
import errno
import heapq
import itertools
import logging
import math
import os
import re
import string
import subprocess
import sys

logger = logging.getLogger()
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('[%(levelname)s] %(asctime)s : %(message)s'))
logger.addHandler(stream_handler)


class Config:
    """
    Hold configuration variable for evaluation. These variables
    should not be changed during evaluation.
    """

    def __init__(self):
        pass

    # TBF file formats.
    comment_marker = "#"
    bod_marker = "#BeginOfDocument"  # mark begin of a document
    eod_marker = "#EndOfDocument"  # mark end of a document
    relation_marker = "@"  # mark start of a relation
    coreference_relation_name = "Coreference"  # mark coreference

    token_joiner = ","
    span_seperator = ";"
    span_joiner = "_"

    missing_attribute_place_holder = "NOT_ANNOTATED"

    default_token_file_ext = ".tab"
    default_token_offset_fields = [2, 3]

    invisible_words = {'the', 'a', 'an', 'I', 'you', 'he', 'she', 'we', 'my',
                       'your', 'her', 'our', 'who', 'where', 'when'}

    # Attribute names, these are the same order as they appear in submissions.
    attribute_names = ["mention_type", "realis_status"]

    # Conll related settings.
    conll_bod_marker = "#begin document"
    conll_eod_marker = "#end document"

    conll_gold_file = None
    conll_sys_file = None

    conll_out = None

    # By default, this reference scorer is shipped with the script. We do it this way so that we can call the script
    # successfully from outside scripts.
    relative_perl_script_path = "/reference-coreference-scorers-8.01/scorer.pl"
    conll_scorer_executable = os.path.dirname(os.path.realpath(__file__)) + relative_perl_script_path

    skipped_metrics = {"ceafm"}

    zero_for_empty_metrics = {"muc"}

    token_miss_msg = "Token ID [%s] not found in token list, the score file provided is incorrect."

    coref_criteria = ((0, "mention_type"),)

    canonicalize_types = True


class EvalMethod:
    """
    Two different evaluation methods
    Char based evaluation is not supported and is only here for
    legacy reasons.
    """

    def __init__(self):
        pass

    Token, Char = range(2)


class MutableConfig:
    """
    Some configuration that might be changed at setup. Default
    values are set here. Do not modify these variables outside
    the Main() function (i.e. outside the setup stage)
    """

    def __init__(self):
        pass

    remove_conll_tmp = False
    eval_mode = EvalMethod.Token
    coref_mention_threshold = 1.0


class EvalState:
    """
    Hold evaluation state variables.
    """

    def __init__(self):
        pass

    gold_docs = {}
    system_docs = {}
    doc_ids_to_score = []
    all_possible_types = set()
    evaluating_index = 0

    doc_mention_scores = []
    doc_coref_scores = []
    overall_coref_scores = {}

    use_new_conll_file = True

    system_id = "_id_"

    @staticmethod
    def advance_index():
        EvalState.evaluating_index += 1

    @staticmethod
    def has_next_doc():
        return EvalState.evaluating_index < len(EvalState.doc_ids_to_score)

    @staticmethod
    def claim_write_flag():
        r = EvalState.use_new_conll_file
        EvalState.use_new_conll_file = False
        return r


def supermakedirs(path, mode=0777):
    """
    A custom makedirs method that get around the umask exception.
    :param path: The path to make directories
    :param mode: The mode of the directory
    :return:
    """
    if not path or os.path.exists(path):
        return []
    (head, tail) = os.path.split(path)
    res = supermakedirs(head, mode)
    os.mkdir(path)
    os.chmod(path, mode)
    res += [path]
    return res


def create_parent_dir(p):
    """
    Create parent directory if not exists.
    :param p: path to file
    :raise:
    """
    try:
        head, tail = os.path.split(p)
        if head != "":
            supermakedirs(head)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Event mention scorer, which conducts token based "
                    "scoring, system and gold standard files should follows "
                    "the token-based format.")
    parser.add_argument("-g", "--gold", help="Golden Standard", required=True)
    parser.add_argument("-s", "--system", help="System output", required=True)
    parser.add_argument("-d", "--comparison_output",
                        help="Compare and help show the difference between "
                             "system and gold")
    parser.add_argument(
        "-o", "--output", help="Optional evaluation result redirects, put eval result to file")
    parser.add_argument(
        "-c", "--coref", help="Eval Coreference result output, need to put the reference"
                              "conll coref scorer in the same folder with this scorer")
    parser.add_argument(
        "-t", "--token_path", help="Path to the directory containing the "
                                   "token mappings file", required=True)
    parser.add_argument(
        "-of", "--offset_field", help="A pair of integer indicates which column we should "
                                      "read the offset in the token mapping file, index starts"
                                      "at 0, default value will be %s" % Config.default_token_offset_fields
    )
    parser.add_argument(
        "-te", "--token_table_extension",
        help="any extension appended after docid of token table files. "
             "Default is [%s]" % Config.default_token_file_ext)
    parser.add_argument("-ct", "--coreference_threshold", type=float, help="Threshold for coreference mention mapping")
    parser.add_argument(
        "-b", "--debug", help="turn debug mode on", action="store_true")

    parser.set_defaults(debug=False)
    args = parser.parse_args()

    if args.debug:
        stream_handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Entered debug mode.")
    else:
        stream_handler.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)

    if args.output is not None:
        out_path = args.output
        create_parent_dir(out_path)
        mention_eval_out = open(out_path, 'w')
        logger.info("Evaluation output will be saved at %s" % out_path)
    else:
        mention_eval_out = sys.stdout
        logger.info("Evaluation output at standard out.")

    if os.path.isfile(args.gold):
        gf = open(args.gold)
    else:
        logger.error("Cannot find gold standard file at " + args.gold)
        sys.exit(1)

    if args.coref is not None:
        Config.conll_out = args.coref
        Config.conll_gold_file = args.coref + "_gold.conll"
        Config.conll_sys_file = args.coref + "_sys.conll"

        logger.info("CoNLL script output will be output at " + Config.conll_out)

        logger.info(
            "Gold and system conll files will generated at " + Config.conll_gold_file + " and " + Config.conll_sys_file)
        # if os.path.exists(Config.conll_tmp_marker):
        #     # Clean up the directory to avoid scoring errors.
        #     remove_conll_tmp()
        # supermakedirs(Config.conll_tmp_marker)

    if os.path.isfile(args.system):
        sf = open(args.system)
    else:
        logger.error("Cannot find system file at " + args.system)
        sys.exit(1)

    diff_out = None
    if args.comparison_output is not None:
        diff_out_path = args.comparison_output
        create_parent_dir(diff_out_path)
        diff_out = open(diff_out_path, 'w')

    token_dir = "."
    if args.token_path is not None:
        if os.path.isdir(args.token_path):
            logger.debug("Will search token files in " + args.token_path)
            token_dir = args.token_path
        else:
            logger.debug("Cannot find given token directory at [%s], "
                         "will try search for current directory" % args.token_path)

    token_offset_fields = Config.default_token_offset_fields
    if args.offset_field is not None:
        try:
            token_offset_fields = [int(x) for x in args.offset_field.split(",")]
        except ValueError as _:
            logger.error("Token offset argument should be two integer with comma in between, i.e. 2,3")

    if args.coreference_threshold is not None:
        MutableConfig.coref_mention_threshold = args.coreference_threshold

    # Read all documents.
    read_all_doc(gf, sf)

    # Take all attribute combinations, which will be used to produce scores.
    attribute_comb = get_attr_combinations(Config.attribute_names)

    logger.info("Coreference mentions need to match %s before consideration" % Config.coref_criteria[0][1])

    while True:
        if not evaluate(token_dir, args.coref, attribute_comb,
                        token_offset_fields, args.token_table_extension,
                        diff_out):
            break

    # Run the CoNLL script on the combined files, which is concatenated from the best alignment of all documents.
    if args.coref is not None:
        logger.debug("Running coreference script for the final scores.")
        run_conll_script(Config.conll_gold_file, Config.conll_sys_file, Config.conll_out)
        # Get the CoNLL scores from output
        EvalState.overall_coref_scores = get_conll_scores(Config.conll_out)

    print_eval_results(mention_eval_out, attribute_comb)

    # Clean up, close files.
    close_if_not_none(diff_out)

    # # Delete temp directory if empty.
    # if MutableConfig.remove_conll_tmp:
    #     remove_conll_tmp()

    logger.info("Evaluation Done.")


def close_if_not_none(f):
    if f is not None:
        f.close()


def run_conll_script(gold_path, system_path, script_out):
    """
    Run the Conll script and output result to the path given
    :param gold_path:
    :param system_path:
    :param script_out: Path to output the scores
    :return:
    """
    logger.info("Running reference CoNLL scorer.")
    with open(script_out, 'wb', 0) as out_file:
        subprocess.call(
            ["perl", Config.conll_scorer_executable, "all", gold_path, system_path],
            stdout=out_file)
    logger.info("Done running CoNLL scorer.")


def get_combined_attribute_header(all_comb, size):
    header_list = [pad_char_before_until("plain", size)]
    for comb in all_comb:
        attr_header = []
        for attr_pair in comb:
            attr_header.append(attr_pair[1])
        header_list.append(pad_char_before_until("+".join(attr_header), size))
    return header_list


def get_cell_width(scored_infos):
    max_doc_name = 0
    for info in scored_infos:
        doc_id = info[5]
        if len(doc_id) > max_doc_name:
            max_doc_name = len(doc_id)
    return max_doc_name


def pad_char_before_until(s, n, c=" "):
    return c * (n - len(s)) + s


def print_eval_results(mention_eval_out, all_attribute_combinations):
    total_gold_mentions = 0
    total_system_mentions = 0
    valid_docs = 0

    plain_global_scores = [0.0] * 4
    attribute_based_global_scores = [[0.0] * 4 for _ in xrange(len(all_attribute_combinations))]

    doc_id_width = get_cell_width(EvalState.doc_mention_scores)

    mention_eval_out.write("========Document Mention Detection Results==========\n")
    small_header_item = "Prec  \tRec  \tF1   "
    attribute_header_list = get_combined_attribute_header(all_attribute_combinations, len(small_header_item))
    small_headers = [small_header_item] * (len(all_attribute_combinations) + 1)
    mention_eval_out.write(pad_char_before_until("", doc_id_width) + "\t" + "\t|\t".join(attribute_header_list) + "\n")
    mention_eval_out.write(pad_char_before_until("Doc ID", doc_id_width) + "\t" + "\t|\t".join(small_headers) + "\n")

    for (tp, fp, attribute_based_counts, num_gold_mentions, num_sys_mentions, docId) in EvalState.doc_mention_scores:
        tp *= 100
        fp *= 100
        prec = safe_div(tp, num_sys_mentions)
        recall = safe_div(tp, num_gold_mentions)
        doc_f1 = compute_f1(prec, recall)

        attribute_based_doc_scores = []

        for comb_index, comb in enumerate(all_attribute_combinations):
            counts = attribute_based_counts[comb_index]
            attr_tp = counts[0] * 100
            attr_fp = counts[1] * 100
            attr_prec = safe_div(attr_tp, num_sys_mentions)
            attr_recall = safe_div(attr_tp, num_gold_mentions)
            attr_f1 = compute_f1(attr_prec, attr_recall)

            attribute_based_doc_scores.append("%.2f\t%.2f\t%.2f" % (attr_prec, attr_recall, attr_f1))

            for score_index, score in enumerate([attr_tp, attr_fp, attr_prec, attr_recall]):
                if not math.isnan(score):
                    attribute_based_global_scores[comb_index][score_index] += score

        mention_eval_out.write(
            "%s\t%.2f\t%.2f\t%.2f\t|\t%s\n" % (
                pad_char_before_until(docId, doc_id_width), prec, recall, doc_f1,
                "\t|\t".join(attribute_based_doc_scores)))

        if math.isnan(recall):
            # gold produce no mentions, do nothing
            pass
        elif math.isnan(prec):
            # system produce no mentions, accumulate denominator
            logger.warning('System produce nothing for document [%s], assigning 0 scores' % docId)
            valid_docs += 1
            total_gold_mentions += num_gold_mentions
        else:
            valid_docs += 1
            total_gold_mentions += num_gold_mentions
            total_system_mentions += num_sys_mentions

            for score_index, score in enumerate([tp, fp, prec, recall]):
                plain_global_scores[score_index] += score

    if len(EvalState.doc_coref_scores) > 0:
        mention_eval_out.write("\n\n========Document Mention Corefrence Results (CoNLL Average)==========\n")
        for coref_score, doc_id in EvalState.doc_coref_scores:
            mention_eval_out.write("%s\t%.2f\n" % (doc_id, coref_score))

    plain_average_scores = get_averages(plain_global_scores, total_gold_mentions, total_system_mentions, valid_docs)

    mention_eval_out.write("\n=======Final Mention Detection Results=========\n")
    max_attribute_name_width = len(max(attribute_header_list, key=len))
    attributes_name_header = pad_char_before_until("Attributes", max_attribute_name_width)

    final_result_big_header = ["Micro Average", "Macro Average"]

    mention_eval_out.write(
        pad_char_before_until("", max_attribute_name_width, " ") + "\t" + "\t".join(
            [pad_char_before_until(h, len(small_header_item)) for h in final_result_big_header]) + "\n")
    mention_eval_out.write(attributes_name_header + "\t" + "\t".join([small_header_item] * 2) + "\n")
    mention_eval_out.write(pad_char_before_until(attribute_header_list[0], max_attribute_name_width) + "\t" + "\t".join(
        "%.2f" % f for f in plain_average_scores) + "\n")
    for attr_index, attr_based_score in enumerate(attribute_based_global_scores):
        attr_average_scores = get_averages(attr_based_score, total_gold_mentions, total_system_mentions, valid_docs)
        mention_eval_out.write(
            pad_char_before_until(attribute_header_list[attr_index + 1], max_attribute_name_width) + "\t" + "\t".join(
                "%.2f" % f for f in attr_average_scores) + "\n")

    if len(EvalState.overall_coref_scores) > 0:
        mention_eval_out.write("\n=======Final Mention Coreference Results=========\n")
        conll_average = 0.0
        for metric, score in EvalState.overall_coref_scores.iteritems():
            formatter = "Metric : %s\tScore\t%.2f\n"
            if metric in Config.skipped_metrics:
                formatter = "Metric : %s\tScore\t%.2f *\n"
            mention_eval_out.write(formatter % (metric, score))
            conll_average += score
        mention_eval_out.write(
            "Overall Average CoNLL score\t%.2f\n" % (conll_average / len(EvalState.overall_coref_scores)))
        mention_eval_out.write("\n* Score not included for final CoNLL score.\n")

        if mention_eval_out is not None:
            mention_eval_out.flush()
        if not mention_eval_out == sys.stdout:
            mention_eval_out.close()


def get_averages(scores, num_gold, num_sys, num_docs):
    micro_prec = safe_div(scores[0], num_sys)
    micro_recall = safe_div(scores[0], num_gold)
    micro_f1 = compute_f1(micro_prec, micro_recall)
    macro_prec = safe_div(scores[2], num_docs)
    macro_recall = safe_div(scores[3], num_docs)
    macro_f1 = compute_f1(macro_prec, macro_recall)
    return micro_prec, micro_recall, micro_f1, macro_prec, macro_recall, macro_f1


def read_token_ids(token_dir, g_file_name, provided_token_ext, token_offset_fields):
    tf_ext = Config.default_token_file_ext if provided_token_ext is None else provided_token_ext

    invisible_ids = set()
    id2token = {}
    id2span = {}

    token_file_path = os.path.join(token_dir, g_file_name + tf_ext)

    logger.debug("Reading token for " + g_file_name)

    try:
        token_file = open(token_file_path)

        # Discard the header.
        # _ = token_file.readline()

        for tline in token_file:
            fields = tline.rstrip().split("\t")
            if len(fields) < 4:
                logger.error("Weird token line " + tline)
                continue

            token = fields[1].lower().strip().rstrip()
            token_id = fields[0]

            id2token[token_id] = token

            try:
                token_span = (int(fields[token_offset_fields[0]]), int(fields[token_offset_fields[1]]))
                id2span[token_id] = token_span
            except ValueError as _:
                logger.error("Token file is wrong at for file [%s], cannot parse token span here." % g_file_name)
                logger.error("  ---> %s" % tline)
                logger.error(
                    "Field %d and Field %d are not integer spans" % (token_offset_fields[0], token_offset_fields[1]))

            if token in Config.invisible_words:
                invisible_ids.add(token_id)

    except IOError:
        logger.error(
            "Cannot find token file for doc [%s] at [%s], "
            "will use empty invisible words list" % (g_file_name, token_file_path))
        pass

    return invisible_ids, id2token, id2span


def safe_div(n, dn):
    return n / dn if dn > 0 else float('nan')


def compute_f1(p, r):
    return safe_div(2 * p * r, (p + r))


def read_all_doc(gf, sf):
    """
    Read all the documents, collect the document ids that are shared by both gold and system. It will populate the
    gold_docs and system_docs, stored as map from doc id to raw annotation strings.

    The document ids considered to be scored are those presented in the gold documents.

    TODO
    This is not particularly optimized and assumes the system response and gold response file can be fit into memory.

    :param gf: Gold standard file
    :param sf:  System response file
    :return:
    """
    EvalState.gold_docs, _ = read_docs_with_doc_id_and_name(gf)
    EvalState.system_docs, EvalState.system_id = read_docs_with_doc_id_and_name(sf)

    g_doc_ids = EvalState.gold_docs.keys()
    s_doc_ids = EvalState.system_docs.keys()

    g_id_set = set(g_doc_ids)
    s_id_set = set(s_doc_ids)

    common_id_set = g_id_set.intersection(s_id_set)

    g_minus_s = g_id_set - common_id_set
    s_minus_g = s_id_set - common_id_set

    if len(g_minus_s) > 0:
        logger.warning("The following document are not found in system but in gold standard")
        for d in g_minus_s:
            logger.warning("  - " + d)

    if len(s_minus_g) > 0:
        logger.warning("\tThe following document are not found in gold standard but in system")
        for d in s_minus_g:
            logger.warning("  - " + d)

    if len(common_id_set) == 0:
        logger.warning("No document to score, file names are all different!")

    EvalState.doc_ids_to_score = sorted(g_id_set)


def read_docs_with_doc_id_and_name(f):
    """
    Parse file into a map from doc id to mention and relation raw strings
    :param f: The annotation file
    :return: A map from doc id to corresponding mention and relation annotations, which are stored as raw string
    """
    all_docs = {}
    mention_lines = []
    relation_lines = []
    doc_id = ""
    run_id = os.path.basename(f.name)
    while True:
        line = f.readline()
        if not line:
            break
        line = line.strip().rstrip()

        if line.startswith(Config.comment_marker):
            if line.startswith(Config.bod_marker):
                doc_id = line[len(Config.bod_marker):].strip()
            elif line.startswith(Config.eod_marker):
                all_docs[doc_id] = mention_lines, relation_lines
                mention_lines = []
                relation_lines = []
        elif line.startswith(Config.relation_marker):
            relation_lines.append(line[len(Config.relation_marker):].strip())
        elif line == "":
            pass
        else:
            mention_lines.append(line)

    return all_docs, run_id


def get_next_doc():
    """
    Get next document pair of gold standard and system response.
    :return: A tuple of 4 element
        (has_next, gold_annotation, system_annotation, doc_id)
    """
    if EvalState.has_next_doc():  # a somewhat redundant check
        doc_id = EvalState.doc_ids_to_score[EvalState.evaluating_index]
        EvalState.advance_index()
        if doc_id in EvalState.system_docs:
            return True, EvalState.gold_docs[doc_id], EvalState.system_docs[doc_id], doc_id, EvalState.system_id
        else:
            return True, EvalState.gold_docs[doc_id], ([], []), doc_id, EvalState.system_id
    else:
        logger.error("Reaching end of all documents")
        return False, ([], []), ([], []), "End_Of_Documents"


def parse_spans(s):
    """
    Method to parse the character based span
    """
    span_strs = s.split(Config.span_seperator)
    spans = []
    for span_strs in span_strs:
        span = list(map(int, span_strs.split(Config.span_joiner)))
        spans.append(span)
    return spans


def parse_token_ids(s, invisible_ids):
    """
     Method to parse the token ids (instead of a span).
    :param s: The input token id field string.
    :param invisible_ids: Ids that should be regarded as invisible.
    :return: The token ids and filtered token ids.
    """
    filtered_token_ids = set()
    original_token_ids = s.split(Config.token_joiner)
    for token_id in original_token_ids:
        if token_id not in invisible_ids:
            filtered_token_ids.add(token_id)
        else:
            logger.debug("Token Id %s is filtered" % token_id)
            pass
    return filtered_token_ids, original_token_ids


def parse_token_based_line(l, invisible_ids):
    """
    Parse the line, get the token ids, remove invisible ones.
    :param l: A line in the tbf file.
    :param invisible_ids: Set of invisible ids to remove.
    """
    fields = l.split("\t")
    num_attributes = len(Config.attribute_names)
    if len(fields) < 5 + num_attributes:
        terminate_with_error("System line has too few fields:\n ---> %s" % l)
    token_ids, original_token_ids = parse_token_ids(fields[3], invisible_ids)
    attributes = [canonicalize_string(a) for a in fields[5:5 + num_attributes]]
    return fields[2], token_ids, attributes, original_token_ids, fields[4]


def canonicalize_string(str):
    if Config.canonicalize_types:
        return "".join(str.lower().split()).translate(string.maketrans("", ""), string.punctuation)
    else:
        return str


def parse_line(l, eval_mode, invisible_ids):
    return parse_token_based_line(l, invisible_ids)


def parse_relation(relation_line):
    """
    Parse the relation as a tuple.
    :param relation_line: the relation line from annotation
    :return:
    """
    parts = relation_line.split("\t")
    relation_arguments = parts[2].split(",")
    return parts[0], parts[1], relation_arguments


def span_overlap(span1, span2):
    """
    Compute the number of characters that overlaps
    :param span1:
    :param span2:
    :return: number of overlapping spans
    """
    if span1[1] > span2[0] and span1[0] < span2[1]:
        # find left end
        left_end = span1[0] if span1[0] < span2[0] else span2[0]
        # find right end
        right_end = span1[1] if span1[1] > span2[1] else span2[1]
        return right_end - left_end
    else:
        # no overlap
        return 0


def compute_token_overlap_score(g_tokens, s_tokens):
    """
    token based overlap score
    It is a set F1 score, which is the same as Dice coefficient
    :param g_tokens: Gold tokens
    :param s_tokens: System tokens
    :return: The Dice Coefficient between two sets of tokens
    """
    total_overlap = 0.0

    for s_token in s_tokens:
        if s_token in g_tokens:
            total_overlap += 1

    glength = len(g_tokens)
    slength = len(s_tokens)

    if total_overlap == 0:
        return 0

    prec = total_overlap / slength
    recall = total_overlap / glength

    return 2 * prec * recall / (prec + recall)


def compute_overlap_score(system_outputs, gold_annos, eval_mode):
    return compute_token_overlap_score(system_outputs, gold_annos)


def get_attr_combinations(attr_names):
    """
    Generate all possible combination attributes.
    :param attr_names: List of attribute names
    :return:
    """
    attribute_names_with_id = list(enumerate(attr_names))
    comb = []
    for L in range(1, len(attribute_names_with_id) + 1):
        comb.extend(itertools.combinations(attribute_names_with_id, L))
    logger.debug("Will score on the following attribute combinations : ")
    logger.debug(", ".join([str(x) for x in comb]))
    return comb


def attribute_based_match(target_attributes, gold_attrs, sys_attrs, doc_id):
    """
    Return whether the two sets of attributes match on all the given attributes
    :param target_attributes: The target attributes to check
    :param gold_attrs: Gold standard attributes
    :param sys_attrs: System response attributes
    :param doc_id: Document ID, used mainly for logging
    :return: True if two sets of attributes matches on given attributes
    """
    for (attribute_index, attribute_name) in target_attributes:
        gold_attr = gold_attrs[attribute_index]
        if gold_attr == Config.missing_attribute_place_holder:
            logger.warning(
                "Found one attribute [%s] in file [%s] not annotated, give full credit to all system." % (
                    Config.attribute_names[attribute_index], doc_id))
            continue
        if gold_attr != sys_attrs[attribute_index]:
            return False
    return True


def write_if_provided(diff_out, text):
    if diff_out is not None:
        diff_out.write(text)


def write_gold_and_system_mappings(doc_id, system_id, assigned_gold_2_system_mapping, gold_mention_table,
                                   system_mention_table, diff_out):
    mapped_system_mentions = set()

    for gold_index, (system_index, score) in enumerate(assigned_gold_2_system_mapping):
        score_str = "%.2f" % score if gold_index >= 0 and system_index >= 0 else "-"

        gold_info = "-"
        if gold_index != -1:
            gold_spans, gold_attributes, gold_mention_id, gold_origin_spans = gold_mention_table[gold_index]
            gold_info = "%s\t%s\t%s" % (gold_mention_id, ",".join(gold_origin_spans), "\t".join(gold_attributes))

        sys_info = "-"
        if system_index != -1:
            system_spans, system_attributes, sys_mention_id, sys_origin_spans = system_mention_table[system_index]
            sys_info = "%s\t%s\t%s" % (sys_mention_id, ",".join(sys_origin_spans), "\t".join(system_attributes))
            mapped_system_mentions.add(system_index)

        write_if_provided(diff_out, "%s\t%s\t|\t%s\t%s\n" % (system_id, gold_info, sys_info, score_str))

    # Write out system mentions that does not map to anything.
    for system_index, (system_spans, system_attributes, sys_mention_id, sys_origin_spans) in enumerate(
            system_mention_table):
        if system_index not in mapped_system_mentions:
            sys_info = "%s\t%s\t%s" % (sys_mention_id, ",".join(sys_origin_spans), "\t".join(system_attributes))
            write_if_provided(diff_out, "%s\t%s\t|\t%s\t%s\n" % (system_id, "-", sys_info, "-"))


def write_gold_and_system_corefs(diff_out, gold_coref, sys_coref, gold_id_2_text, sys_id_2_text):
    for c in gold_coref:
        write_if_provided(diff_out, "@coref\tgold\t%s\n" % ",".join([c + ":" + gold_id_2_text[c] for c in c[2]]))
    for c in sys_coref:
        write_if_provided(diff_out, "@coref\tsystem\t%s\n" % ",".join([c + ":" + sys_id_2_text[c] for c in c[2]]))


def get_tp_greedy(all_gold_system_mapping_scores, all_attribute_combinations, gold_mention_table,
                  system_mention_table, doc_id):
    tp = 0.0  # span only true positive
    attribute_based_tps = [0.0] * len(all_attribute_combinations)  # attribute based true positive

    # For mention only and attribute augmented true positives.
    greedy_all_attributed_mapping = [[(-1, 0)] * len(gold_mention_table) for _ in
                                     xrange(len(all_attribute_combinations))]
    greedy_mention_only_mapping = [(-1, 0)] * len(gold_mention_table)

    # Record already mapped system index for each case.
    mapped_system = set()
    mapped_gold = set()
    mapped_system_with_attributes = [set() for _ in xrange(len(all_attribute_combinations))]
    mapped_gold_with_attributes = [set() for _ in xrange(len(all_attribute_combinations))]

    while len(all_gold_system_mapping_scores) != 0:
        neg_mapping_score, system_index, gold_index = heapq.heappop(all_gold_system_mapping_scores)
        score = -neg_mapping_score
        if system_index not in mapped_system and gold_index not in mapped_gold:
            tp += score
            greedy_mention_only_mapping[gold_index] = (system_index, score)
            mapped_system.add(system_index)
            mapped_gold.add(gold_index)

        # For each attribute combination.
        gold_attrs = gold_mention_table[gold_index][1]
        system_attrs = system_mention_table[system_index][1]
        for attr_comb_index, attr_comb in enumerate(all_attribute_combinations):
            if system_index not in mapped_system_with_attributes[attr_comb_index] and gold_index not in \
                    mapped_gold_with_attributes[attr_comb_index]:
                if attribute_based_match(attr_comb, gold_attrs, system_attrs, doc_id):
                    attribute_based_tps[attr_comb_index] += score
                    greedy_all_attributed_mapping[attr_comb_index][gold_index] = (system_index, score)
                    mapped_system_with_attributes[attr_comb_index].add(system_index)
                    mapped_gold_with_attributes[attr_comb_index].add(gold_index)
    return tp, attribute_based_tps, greedy_mention_only_mapping, greedy_all_attributed_mapping


def get_or_terminate(dictionary, key, error_msg):
    if key in dictionary:
        return dictionary[key]
    else:
        terminate_with_error(error_msg)


def terminate_with_error(msg):
    logger.error(msg)
    logger.error("Scorer terminate with error.")
    sys.exit(1)


def check_unique(keys):
    return len(keys) == len(set(keys))


def evaluate(token_dir, coref_out, all_attribute_combinations,
             token_offset_fields, token_file_ext, diff_out):
    """
    Conduct the main evaluation steps.
    :param token_dir:
    :param coref_out:
    :param all_attribute_combinations:
    :param token_offset_fields:
    :param token_file_ext:
    :param diff_out:
    :return:
    """
    if EvalState.has_next_doc():
        res, (g_mention_lines, g_relation_lines), (
            s_mention_lines, s_relation_lines), doc_id, system_id = get_next_doc()
    else:
        return False

    logger.info("Evaluating Document %s" % doc_id)

    eval_mode = MutableConfig.eval_mode

    invisible_ids, id2token, id2span = read_token_ids(token_dir, doc_id, token_file_ext, token_offset_fields)

    # system_id = ""
    # if len(s_mention_lines) > 0:
    #     fields = s_mention_lines[0].split("\t")
    #     if len(fields) > 0:
    #         system_id = fields[0]

    # Parse the lines and save them as a table from id to content.
    system_mention_table = []
    gold_mention_table = []

    # Save the raw text for visualization.
    sys_id_2_text = {}
    gold_id_2_text = {}

    logger.debug("Reading gold and response mentions.")

    mention_ids = []
    for sl in s_mention_lines:
        sys_mention_id, sys_spans, sys_attributes, origin_sys_spans, text = parse_line(sl, eval_mode, invisible_ids)
        system_mention_table.append((sys_spans, sys_attributes, sys_mention_id, origin_sys_spans))
        EvalState.all_possible_types.add(sys_attributes[0])
        mention_ids.append(sys_mention_id)
        sys_id_2_text[sys_mention_id] = text

    if not check_unique(mention_ids):
        logger.error("Duplicated mention id for doc %s" % doc_id)
        return False

    for gl in g_mention_lines:
        gold_mention_id, gold_spans, gold_attributes, origin_gold_spans, text = parse_line(gl, eval_mode, invisible_ids)
        gold_mention_table.append((gold_spans, gold_attributes, gold_mention_id, origin_gold_spans))
        EvalState.all_possible_types.add(gold_attributes[0])
        gold_id_2_text[gold_mention_id] = text

    # Store list of mappings with the score as a priority queue. Score is stored using negative for easy sorting.
    all_gold_system_mapping_scores = []

    # Debug purpose printing.
    print_score_matrix = False

    logger.debug("Computing overlap scores.")
    for system_index, (sys_spans, sys_attributes, sys_mention_id, _) in enumerate(system_mention_table):
        if print_score_matrix:
            print system_index,
        for index, (gold_spans, gold_attributes, gold_mention_id, _) in enumerate(gold_mention_table):
            overlap = compute_overlap_score(gold_spans, sys_spans, eval_mode)
            if len(gold_spans) == 0:
                logger.warning("Found empty span gold standard at doc : %s, mention : %s" % (doc_id, gold_mention_id))

            if print_score_matrix:
                print "%.1f" % overlap,

            if overlap > 0:
                # maintaining a max heap based on overlap score
                heapq.heappush(all_gold_system_mapping_scores, (-overlap, system_index, index))
        if print_score_matrix:
            print

    greedy_tp, greed_attribute_tps, greedy_mention_only_mapping, greedy_all_attributed_mapping = get_tp_greedy(
        all_gold_system_mapping_scores, all_attribute_combinations, gold_mention_table,
        system_mention_table, doc_id)

    write_if_provided(diff_out, Config.bod_marker + " " + doc_id + "\n")
    if diff_out is not None:
        # Here if you change the mapping used, you will see what's wrong on different level!
        write_gold_and_system_mappings(doc_id, system_id, greedy_mention_only_mapping, gold_mention_table,
                                       system_mention_table, diff_out)

    attribute_based_fps = [0.0] * len(all_attribute_combinations)
    for attribute_comb_index, abtp in enumerate(greed_attribute_tps):
        attribute_based_fps[attribute_comb_index] = len(s_mention_lines) - abtp

    # Unmapped system mentions and the partial scores are considered as false positive.
    fp = len(s_mention_lines) - greedy_tp

    EvalState.doc_mention_scores.append((greedy_tp, fp, zip(greed_attribute_tps, attribute_based_fps),
                                         len(g_mention_lines), len(s_mention_lines), doc_id))

    # Select a computed mapping, we currently select the mapping based on mention type. This means that in order to get
    # coreference right, your mention type should also be right.
    selected_one2one_mapping = None
    for attribute_comb_index, attribute_comb in enumerate(all_attribute_combinations):
        if attribute_comb == Config.coref_criteria:
            selected_one2one_mapping = greedy_all_attributed_mapping[attribute_comb_index]
            logger.debug("Select mapping that matches criteria [%s]" % (Config.coref_criteria[0][1]))
            break

    if selected_one2one_mapping is None:
        # In case when we don't do attribute scoring.
        selected_one2one_mapping = greedy_mention_only_mapping

    if coref_out is not None:
        logger.debug("Start preparing coreference files.")

        gold_corefs = [coref for coref in [parse_relation(l) for l in g_relation_lines] if
                       coref[0] == Config.coreference_relation_name]

        sys_corefs = [coref for coref in [parse_relation(l) for l in s_relation_lines] if
                      coref[0] == Config.coreference_relation_name]

        # Prepare CoNLL style coreference input for this document.
        conll_converter = ConllConverter(id2token, doc_id, system_id)
        gold_conll_lines, sys_conll_lines = conll_converter.prepare_conll_lines(gold_corefs, sys_corefs,
                                                                                gold_mention_table,
                                                                                system_mention_table,
                                                                                selected_one2one_mapping,
                                                                                MutableConfig.coref_mention_threshold)

        # If we are selecting among multiple mappings, it is easy to write in our file.
        write_mode = 'w' if EvalState.claim_write_flag() else 'a'
        g_conll_out = open(Config.conll_gold_file, write_mode)
        s_conll_out = open(Config.conll_sys_file, write_mode)
        g_conll_out.writelines(gold_conll_lines)
        s_conll_out.writelines(sys_conll_lines)

        if diff_out is not None:
            write_gold_and_system_corefs(diff_out, gold_corefs, sys_corefs, gold_id_2_text, sys_id_2_text)

    write_if_provided(diff_out, Config.eod_marker + " " + "\n")

    return True


def get_conll_scores(score_path):
    metric = "UNKNOWN"

    scores_by_metric = {}

    with open(score_path, 'r') as f:
        for l in f:
            if l.startswith("METRIC"):
                metric = l.split()[-1].strip().strip(":")
            if l.startswith("Coreference: ") or l.startswith("BLANC: "):
                f1 = float(l.split("F1:")[-1].strip().strip("%"))
                scores_by_metric[metric] = f1

    return scores_by_metric


def natural_order(key):
    """
    Compare order based on the numeric values in key, for example, 't1 < t2'
    :param key:
    :return:
    """
    convert = lambda text: int(text) if text.isdigit() else text
    return [convert(c) for c in re.split('([0-9]+)', key)]


def transitive_not_resolved(clusters):
    """
    Check whether transitive closure is resolved between clusters.
    :param clusters:
    :return: False if not resolved
    """
    ids = clusters.keys()
    for i in range(0, len(ids) - 1):
        for j in range(i + 1, len(ids)):
            if len(clusters[i].intersection(clusters[j])) != 0:
                logger.error(
                    "Non empty intersection between clusters found. Please resolve transitive closure before submit.")
                logger.error(clusters[i])
                logger.error(clusters[j])
                return True
    return False


def add_to_multi_map(multi_map, key, val):
    """
    Utility class to make the map behave like a multi-map, a key is mapped to multiple values
    :param multi_map: A map to insert to
    :param key:
    :param val:
    :return:
    """
    if key not in multi_map:
        multi_map[key] = []
    multi_map[key].append(val)


def within_cluster_span_duplicate(cluster, event_mention_id_2_sorted_tokens):
    """
    Check whether there is within cluster span duplication, i.e., two mentions in the same cluster have the same span,
    this is not allowed.
    :param cluster: The cluster
    :param event_mention_id_2_sorted_tokens: A map from mention id to span (in terms of tokens)
    :return:
    """
    span_map = {}
    for eid in cluster:
        span = tuple(get_or_terminate(event_mention_id_2_sorted_tokens, eid,
                                      "Cluster contains event that is not in mention list : [%s]" % eid))
        if span in span_map:
            logger.error("Span within the same cluster cannot be the same.")
            logger.error("%s->[%s]" % (eid, ",".join(span)))
            logger.error("%s->[%s]" % (span_map[span], ",".join(span)))
            return True
        else:
            span_map[span] = eid


class ConllConverter:
    def __init__(self, id2token, doc_id, system_id):
        """
        :param id2token: a dict, map from token id to its string
        :param doc_id: the document id
        :param system_id: The id of the participant system
        :return:
        """
        self.id2token = id2token
        self.doc_id = doc_id
        self.system_id = system_id

    @staticmethod
    def create_aligned_tables(gold_2_system_one_2_one_mapping, gold_mention_table, system_mention_table,
                              threshold=1.0):
        """
        Create coreference alignment for gold and system mentions by taking an alignment threshold.
        :param gold_2_system_one_2_one_mapping: Gold index to (system index, score) mapping, indexed by gold index.
        :param gold_mention_table:
        :param system_mention_table:
        :param threshold:
        :return:
        """
        aligned_gold_table = []
        aligned_system_table = []

        aligned_system_mentions = set()

        for gold_index, system_aligned in enumerate(gold_2_system_one_2_one_mapping):
            aligned_gold_table.append((gold_mention_table[gold_index][0], gold_mention_table[gold_index][2]))
            if system_aligned is None:
                # Indicate nothing aligned with this gold mention.
                aligned_system_table.append(None)
                continue
            system_index, alignment_score = system_aligned
            if alignment_score >= threshold:
                aligned_system_table.append(
                    (system_mention_table[system_index][0], system_mention_table[system_index][2]))
                aligned_system_mentions.add(system_index)
            else:
                aligned_system_table.append(None)

        for system_index, system_mention in enumerate(system_mention_table):
            # Add unaligned system mentions.
            if system_index not in aligned_system_mentions:
                aligned_gold_table.append(None)
                aligned_system_table.append(
                    (system_mention_table[system_index][0], system_mention_table[system_index][2]))

        return aligned_gold_table, aligned_system_table

    @staticmethod
    def generate_temp_conll_file_base(temp_header, system_id, doc_id):
        return "%s_%s_%s" % (temp_header, system_id, doc_id)

    @staticmethod
    def extract_token_map(mention_table):
        event_mention_id2sorted_tokens = {}
        for mention in mention_table:
            tokens = sorted(mention[0], key=natural_order)
            event_mention_id2sorted_tokens[mention[2]] = tokens
        return event_mention_id2sorted_tokens

    def prepare_conll_lines(self, gold_corefs, sys_corefs, gold_mention_table, system_mention_table,
                            gold_2_system_one_2_one_mapping, threshold=1.0):
        """
        Convert to ConLL style lines
        :param gold_corefs: gold coreference chain
        :param sys_corefs: system coreferenc chain
        :param gold_mention_table:  gold mention table
        :param system_mention_table: system mention table
        :param gold_2_system_one_2_one_mapping: a mapping between gold and system
        :param threshold: To what extent we treat two mention can be aligned, default 1 for exact match
        :return:
        """
        aligned_gold_table, aligned_system_table = self.create_aligned_tables(gold_2_system_one_2_one_mapping,
                                                                              gold_mention_table,
                                                                              system_mention_table,
                                                                              threshold)
        logger.debug("Preparing CoNLL files using mapping threhold %.2f" % threshold)

        gold_conll_lines = self.prepare_lines(gold_corefs, aligned_gold_table,
                                              self.extract_token_map(gold_mention_table))

        sys_conll_lines = self.prepare_lines(sys_corefs, aligned_system_table,
                                             self.extract_token_map(system_mention_table))

        if not gold_conll_lines:
            terminate_with_error("Gold standard has data problem for doc [%s], please refer to log. Quitting..."
                                 % self.doc_id)

        if not sys_conll_lines:
            terminate_with_error("System has data problem for doc [%s], please refer to log. Quitting..."
                                 % self.doc_id)

        return gold_conll_lines, sys_conll_lines

    def prepare_lines(self, corefs, mention_table, event_mention_id2sorted_tokens):
        clusters = {}
        for cluster_id, one_coref_cluster in enumerate(corefs):
            clusters[cluster_id] = set(one_coref_cluster[2])

        if transitive_not_resolved(clusters):
            return False

        singleton_cluster_id = len(corefs)

        coref_fields = []
        for mention in mention_table:
            if mention is None:
                coref_fields.append(("None", "-"))
                continue

            event_mention_id = mention[1]

            non_singleton_cluster_id = None

            for cluster_id, cluster_mentions in clusters.iteritems():
                if event_mention_id in cluster_mentions:
                    non_singleton_cluster_id = cluster_id
                    break

            if non_singleton_cluster_id is not None:
                output_cluster_id = non_singleton_cluster_id
            else:
                output_cluster_id = singleton_cluster_id
                singleton_cluster_id += 1

            merged_mention_str = "_".join([get_or_terminate(self.id2token, tid, Config.token_miss_msg % tid)
                                           for tid in event_mention_id2sorted_tokens[event_mention_id]])

            coref_fields.append((merged_mention_str, output_cluster_id))

        for cluster_id, cluster in clusters.iteritems():
            if within_cluster_span_duplicate(cluster, event_mention_id2sorted_tokens):
                return False

        lines = []

        lines.append("%s (%s); part 000%s" % (Config.conll_bod_marker, self.doc_id, os.linesep))
        for index, (merged_mention_str, cluster_id) in enumerate(coref_fields):
            lines.append("%s\t%s\t%s\t(%s)\n" % (self.doc_id, index, merged_mention_str, cluster_id))
        lines.append(Config.conll_eod_marker + os.linesep)

        return lines


if __name__ == "__main__":
    main()

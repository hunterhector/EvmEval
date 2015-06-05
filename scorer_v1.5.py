#!/usr/bin/python

"""
    A simple scorer that reads the CMU Event Mention Format (tbf)
    data and produce a mention based F-Scores

    It could also call the CoNLL coreference implementation and
    produce coreference results

    This scorer also require token files to conduct evaluation

    Author: Zhengzhong Liu ( liu@cs.cmu.edu )
"""
# Change log v1.5:
# 1. Given that the CoNLL scorer only score exact matched mentions, we convert input format
#    to a simplified form. We produce a mention mappings and feed to the scorer.
#    In case of double tagging, there are multiple way of mention mappings, we will produce all
#    possible ways, and use the highest final score mapping.
# 2. Fix a bug that crashes when generating text output from empty responses

# Change log v1.4:
# 1. global mention span check: do not allow duplicate mention span with same type
# 2. within cluster mention span check : do not allow duplicate span in one cluster

# Change log v1.3:
# 1. add ability to convert input format to conll format, and feed it to the coreference resolver
# 2. clean up and remove global variables

# Change log v1.2:
# 1. Change attribute scoring, combine it with mention span scoring
# 2. Precision for span is divided by #SYS instead of TP + FP
# 3. Plain text summary is made better
# 4. Separate the visualization code out into anther file

# Change log v1.1:
# 1. If system produce no mentions, the scorer should penalize it instead of ignore it
# 2. Enhance the output of the comparison file, add the system actual output side by side for easy debug
# 3. Add the ability to compare system and gold mentions using Brat embedded visualization
# 4. For realis type not annotated, give full credit as long as system give a result
# 5. Add more informative error message

import math
import errno
import argparse
import logging
import sys
import os
import heapq
import itertools
import re
import subprocess
import copy

logger = logging.getLogger()
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s : %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

comment_marker = "#"
bod_marker = "#BeginOfDocument"  # mark begin of a document
eod_marker = "#EndOfDocument"  # mark end of a document
relation_marker = "@"  # mark start of a relation
coreference_relation_name = "Coreference"  # mark coreference

conll_scorer_executable = "./reference-coreference-scorers-8.01/scorer.pl"

conll_bod_marker = "#begin document"
conll_eod_marker = "#end document"

default_token_file_ext = ".tab"
default_token_offset_fields = [2, 3]

# run this on an annotation to confirm
invisible_words = {'the', 'a', 'an', 'I', 'you', 'he', 'she', 'we', 'my',
                   'your', 'her', 'our', 'who', 'what', 'where', 'when'}

# attribute names
attribute_names = ["mention_type", "realis_status"]

gold_docs = {}
system_docs = {}
doc_ids_to_score = []
all_possible_types = set()
evaluating_index = 0

doc_scores = []

token_joiner = ","
span_seperator = ";"
span_joiner = "_"

missingAttributePlaceholder = "NOT_ANNOTATED"

temp_gold_conll_file_name = "conll-gold.tmp.conll"
temp_sys_conll_file_name = "conll-sys.tmp.conll"


class EvalMethod:
    Token, Char = range(2)


def create_parent_dir(p):
    """
    create parent directory if not exists
    :param p: path to file
    :raise:
    """
    try:
        head, tail = os.path.split(p)
        if head != "":
            os.makedirs(head)
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
                                      "at 0, default value will be %s" % default_token_offset_fields
    )
    parser.add_argument(
        "-te", "--token_table_extension",
        help="any extension appended after docid of token table files. "
             "Default is [%s]" % default_token_file_ext)
    parser.add_argument(
        "-b", "--debug", help="turn debug mode on", action="store_true")

    parser.set_defaults(debug=False)
    args = parser.parse_args()

    if args.debug:
        stream_handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
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
        logger.info("Evaluation output at standard out")

    if os.path.isfile(args.gold):
        gf = open(args.gold)
    else:
        logger.error("Cannot find gold standard file at " + args.gold)
        sys.exit(1)

    gold_conll_file_out = None
    sys_conll_file_out = None
    eval_coref = False
    if args.coref is not None:
        logger.info("Coreference result will be output at " + args.coref)
        gold_conll_file_out = open(temp_gold_conll_file_name, 'w')
        sys_conll_file_out = open(temp_sys_conll_file_name, 'w')
        eval_coref = True

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

    token_offset_fields = default_token_offset_fields
    if args.offset_field is not None:
        try:
            token_offset_fields = [int(x) for x in args.offset_field.split(",")]
        except ValueError as _:
            logger.error("Should provide two integer with comma in between")

    # token based eval mode
    eval_mode = EvalMethod.Token
    read_all_doc(gf, sf)

    attribute_comb = get_attr_combinations(attribute_names)

    while True:
        if not evaluate(eval_mode, token_dir, eval_coref, attribute_comb,
                        token_offset_fields, args.token_table_extension,
                        diff_out, gold_conll_file_out, sys_conll_file_out):
            break
    print_eval_results(mention_eval_out, attribute_comb)

    # clean up, close files
    close_if_not_none(gold_conll_file_out)
    close_if_not_none(sys_conll_file_out)
    close_if_not_none(diff_out)

    # run conll coreference script
    if eval_coref:
        run_conll_script(args.coref)

    logger.info("Evaluation Done.")


def close_if_not_none(f):
    if f is not None:
        f.close()


def run_conll_script(coref_out):
    logger.info("Running Conll Evaluation reference-coreference-scorers")
    with open(coref_out, 'wb', 0) as out_file:
        subprocess.call(
            ["perl", conll_scorer_executable, "all", temp_gold_conll_file_name,
             temp_sys_conll_file_name],
            stdout=out_file)
    logger.info("Coreference Results written to " + coref_out)


def get_combined_attribute_header(all_comb, size):
    header_list = [pad_char_before_until("plain", size)]
    for comb in all_comb:
        # print comb
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

    doc_id_width = get_cell_width(doc_scores)

    mention_eval_out.write("========Document results==========\n")
    small_header_item = "Prec  \tRec  \tF1   "
    attribute_header_list = get_combined_attribute_header(all_attribute_combinations, len(small_header_item))
    small_headers = [small_header_item] * (len(all_attribute_combinations) + 1)
    mention_eval_out.write(pad_char_before_until("", doc_id_width) + "\t" + "\t|\t".join(attribute_header_list) + "\n")
    mention_eval_out.write(pad_char_before_until("Doc ID", doc_id_width) + "\t" + "\t|\t".join(small_headers) + "\n")

    for (tp, fp, attribute_based_counts, num_gold_mentions, num_sys_mentions, docId) in doc_scores:
        tp *= 100
        fp *= 100
        prec = safe_div(tp, num_sys_mentions)
        recall = safe_div(tp, num_gold_mentions)
        doc_f1 = f1(prec, recall)

        attribute_based_doc_scores = []

        for comb_index, comb in enumerate(all_attribute_combinations):
            counts = attribute_based_counts[comb_index]
            attr_tp = counts[0] * 100
            attr_fp = counts[1] * 100
            attr_prec = safe_div(attr_tp, num_sys_mentions)
            attr_recall = safe_div(attr_tp, num_gold_mentions)
            attr_f1 = f1(attr_prec, attr_recall)

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

    plain_average_scores = get_averages(plain_global_scores, total_gold_mentions, total_system_mentions, valid_docs)

    mention_eval_out.write("\n=======Final Results=========\n")
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

    if mention_eval_out is not None:
        mention_eval_out.flush()
        if not mention_eval_out == sys.stdout:
            mention_eval_out.close()


def get_averages(scores, num_gold, num_sys, num_docs):
    micro_prec = safe_div(scores[0], num_sys)
    micro_recall = safe_div(scores[0], num_gold)
    micro_f1 = f1(micro_prec, micro_recall)
    macro_prec = safe_div(scores[2], num_docs)
    macro_recall = safe_div(scores[3], num_docs)
    macro_f1 = f1(macro_prec, macro_recall)
    return micro_prec, micro_recall, micro_f1, macro_prec, macro_recall, macro_f1


def read_token_ids(token_dir, g_file_name, provided_token_ext, token_offset_fields):
    tf_ext = default_token_file_ext if provided_token_ext is None else provided_token_ext

    invisible_ids = set()
    id2token_map = {}
    id2span_map = {}

    token_file_path = os.path.join(token_dir, g_file_name + tf_ext)

    logger.debug("Reading token for " + g_file_name)

    try:
        token_file = open(token_file_path)

        # discard the header
        header = token_file.readline()

        for tline in token_file:
            fields = tline.rstrip().split("\t")
            if len(fields) < 4:
                logger.error("Weird token line " + tline)
                continue

            token = fields[1].lower().strip().rstrip()
            token_id = fields[0]

            id2token_map[token_id] = token

            try:
                token_span = (int(fields[token_offset_fields[0]]), int(fields[token_offset_fields[1]]) + 1)
                id2span_map[token_id] = token_span
            except ValueError as e:
                logger.error("Token file is wrong at for file " + g_file_name)

            if token in invisible_words:
                invisible_ids.add(token_id)

    except IOError:
        logger.error(
            "Cannot find token file for doc [%s] at [%s], "
            "will use empty invisible words list" % (g_file_name, token_file_path))
        pass

    return invisible_ids, id2token_map, id2span_map


def safe_div(n, dn):
    return n / dn if dn > 0 else float('nan')


def f1(p, r):
    return safe_div(2 * p * r, (p + r))


def read_all_doc(gf, sf):
    global gold_docs
    global system_docs
    global doc_ids_to_score
    gold_docs = read_docs_with_doc_id(gf)
    system_docs = read_docs_with_doc_id(sf)

    g_doc_ids = gold_docs.keys()
    s_doc_ids = system_docs.keys()

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

    doc_ids_to_score = sorted(g_id_set)


def read_docs_with_doc_id(f):
    all_docs = {}
    mention_lines = []
    relation_lines = []
    doc_id = ""
    while True:
        line = f.readline()
        if not line:
            break
        line = line.strip().rstrip()

        if line.startswith(comment_marker):
            if line.startswith(bod_marker):
                doc_id = line[len(bod_marker):].strip()
            elif line.startswith(eod_marker):
                all_docs[doc_id] = mention_lines, relation_lines
                mention_lines = []
                relation_lines = []
        elif line.startswith(relation_marker):
            relation_lines.append(line[len(relation_marker):].strip())
        elif line == "":
            pass
        else:
            mention_lines.append(line)

    return all_docs


def has_next_doc():
    return evaluating_index < len(doc_ids_to_score)


def get_next_doc():
    global evaluating_index
    if evaluating_index < len(doc_ids_to_score):
        doc_id = doc_ids_to_score[evaluating_index]
        evaluating_index += 1
        if doc_id in system_docs:
            return True, gold_docs[doc_id], system_docs[doc_id], doc_id
        else:
            return True, gold_docs[doc_id], ([], []), doc_id
    else:
        logger.error("Reaching end of all documents")
        return False, ([], []), ([], []), "End_Of_Documents"


def parse_spans(s):
    """
    Method to parse the character based span
    """
    span_strs = s.split(span_seperator)
    spans = []
    for span_strs in span_strs:
        span = list(map(int, span_strs.split(span_joiner)))
        spans.append(span)
    return spans


def parse_token_ids(s, invisible_ids):
    """
    Method to parse the token ids (instead of a span)
    """
    filtered_token_ids = set()
    for token_id in s.split(token_joiner):
        if token_id not in invisible_ids:
            filtered_token_ids.add(token_id)
        else:
            logger.debug("Token Id %s is filtered" % token_id)
            pass
    return filtered_token_ids


def parse_token_based_line(l, invisible_ids):
    """
    parse the line, get the token ids, remove invisible ones
    """
    fields = l.split("\t")
    num_attributes = len(attribute_names)
    if len(fields) < 5 + num_attributes:
        logger.error("System line too few fields")
    token_ids = parse_token_ids(fields[3], invisible_ids)

    return fields[2], token_ids, fields[5:]


def parse_line(l, eval_mode, invisible_ids):
    return parse_token_based_line(l, invisible_ids)


def parse_relation(relation_line):
    parts = relation_line.split("\t")
    relation_arguments = parts[2].split(",")
    return parts[0], parts[1], relation_arguments


def span_overlap(span1, span2):
    """
    return the number of characters that overlaps
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
    """

    total_overlap = 0.0

    for s_token in s_tokens:
        if s_token in g_tokens:
            total_overlap += 1

    glength = len(g_tokens)
    slength = len(s_tokens)

    if total_overlap == 0:
        return 0

    # alternatively : return total_overlap / (glength + slength)

    prec = total_overlap / slength
    recall = total_overlap / glength

    return 2 * prec * recall / (prec + recall)


def compute_overlap_score(system_outputs, gold_annos, eval_mode):
    return compute_token_overlap_score(system_outputs, gold_annos)


def get_attr_combinations(attr_names):
    attribute_names_with_id = list(enumerate(attr_names))
    comb = []
    for L in range(1, len(attribute_names_with_id) + 1):
        comb.extend(itertools.combinations(attribute_names_with_id, L))
    return comb


def attribute_based_match(attribute_comb, gold_attrs, sys_attrs, doc_id):
    for (attribute_index, attribute_name) in attribute_comb:
        gold_attr = gold_attrs[attribute_index]
        if gold_attr == missingAttributePlaceholder:
            logger.warning(
                "Found one attribute [%s] in file [%s] not annotated, give full credit to all system." % (
                    attribute_names[attribute_index], doc_id))
            continue
        if gold_attr != sys_attrs[attribute_index]:
            return False
    return True


def write_if_provided(diff_out, text):
    if diff_out is not None:
        diff_out.write(text)


def prepare_write_schedule(gold_mention_table, system_mention_table, assigned_gold_2_system_mapping):
    schedule = []
    system_mapped_markers = [False] * len(system_mention_table)
    for gold_index, _ in enumerate(gold_mention_table):
        mapped_system_indices_and_scores = assigned_gold_2_system_mapping[gold_index]
        if len(mapped_system_indices_and_scores) == 0:
            schedule.append((gold_index, -1, -1))
            continue
        mapped_system_sorted_by_index = sorted(mapped_system_indices_and_scores, key=lambda t: t[1])
        for system_index, score in mapped_system_sorted_by_index:
            schedule.append((gold_index, system_index, score))
            system_mapped_markers[system_index] = True

    for system_index, m in enumerate(system_mapped_markers):
        if not m:
            schedule.append((-1, system_index, -1))

    return schedule


def write_gold_and_system_mappings(doc_id, system_id, assigned_gold_2_system_mapping, gold_mention_table,
                                   system_mention_table, diff_out):
    schedule = prepare_write_schedule(gold_mention_table, system_mention_table, assigned_gold_2_system_mapping)
    write_if_provided(diff_out, bod_marker + " " + doc_id + "\n")

    for gold_index, system_index, score in schedule:
        score_str = "%.2f" % score if gold_index >= 0 and system_index >= 0 else "-"

        gold_info = "-"
        if gold_index != -1:
            gold_spans, gold_attributes, gold_mention_id = gold_mention_table[gold_index]
            gold_info = "%s\t%s\t%s" % (gold_mention_id, ",".join(gold_spans), "\t".join(gold_attributes))

        sys_info = "-"
        if system_index != -1:
            system_spans, system_attributes, sys_mention_id = system_mention_table[system_index]
            sys_info = "%s\t%s\t%s" % (sys_mention_id, ",".join(system_spans), "\t".join(system_attributes))

        write_if_provided(diff_out, "%s\t%s\t|\t%s\t%s\n" % (system_id, gold_info, sys_info, score_str))

    write_if_provided(diff_out, eod_marker + " " + "\n")


def generate_all_system_branches(mapped_system_mentions):
    list_of_one_to_one_mappings = []
    first_mapping = {}
    list_of_one_to_one_mappings.append(first_mapping)
    for system_id, mapped_gold_ids in mapped_system_mentions.iteritems():
        do_branch = False
        additional_one_to_one_mappings = []
        if len(mapped_gold_ids) > 1:
            do_branch = True

        for mapping in list_of_one_to_one_mappings:
            if do_branch:
                for mapped_gold_id in mapped_gold_ids[1:]:
                    mapping_branch = copy.deepcopy(mapping)
                    mapping_branch[system_id] = mapped_gold_id
                    additional_one_to_one_mappings.append(mapping_branch)
            mapping[system_id] = mapped_gold_ids[0]
        list_of_one_to_one_mappings.extend(additional_one_to_one_mappings)
    return list_of_one_to_one_mappings


def unify_system_mapping(gold_2_system_many_2_many_mapping, system_mapping_choice):
    gold_2_system_one_2_many_mapping = [[] for _ in xrange(len(gold_2_system_many_2_many_mapping))]
    for gold_index, mapped_system_indices_and_scores in enumerate(
            gold_2_system_many_2_many_mapping):
        for system_index, score in mapped_system_indices_and_scores:
            if system_mapping_choice[system_index] == gold_index:
                gold_2_system_one_2_many_mapping[gold_index].append((system_index, score))
    return gold_2_system_one_2_many_mapping


def get_tp(all_attribute_combinations, gold_2_system_one_2_many_mapping, gold_mention_table, system_mention_table,
           doc_id):
    tp = 0.0
    attribute_based_tps = [0.0] * len(all_attribute_combinations)

    logger.debug("Calculating scores for the following mapping")
    logger.debug(gold_2_system_one_2_many_mapping)

    for gold_index, mapped_system_indices_and_scores in enumerate(
            gold_2_system_one_2_many_mapping):
        if len(mapped_system_indices_and_scores) > 0:
            max_mapping_score = mapped_system_indices_and_scores[0][1]
            tp += max_mapping_score

        gold_attrs = gold_mention_table[gold_index][1]

        for attr_comb_index, attr_comb in enumerate(all_attribute_combinations):
            for system_index, score in mapped_system_indices_and_scores:
                system_attrs = system_mention_table[system_index][1]
                if attribute_based_match(attr_comb, gold_attrs, system_attrs, doc_id):
                    attribute_based_tps[attr_comb_index] += score
                    break

    logger.debug("Number of true positive %.2f" % tp)

    return tp, attribute_based_tps


def terminate_with_error():
    logger.error("Scorer terminate with error")
    sys.exit(1)


def evaluate(eval_mode, token_dir, eval_coref, all_attribute_combinations,
             token_offset_fields, token_file_ext,
             diff_out, gold_conll_file_out, sys_conll_file_out):
    if has_next_doc():
        res, (g_mention_lines, g_relation_lines), (s_mention_lines, s_relation_lines), doc_id = get_next_doc()
    else:
        return False

    invisible_ids, id2token_map, id2span_map = read_token_ids(token_dir, doc_id, token_file_ext, token_offset_fields)

    system_id = ""
    if len(s_mention_lines) > 0:
        fields = s_mention_lines[0].split("\t")
        if len(fields) > 0:
            system_id = fields[0]

    # parse the lines in file
    system_mention_table = []
    gold_mention_table = []

    for sl in s_mention_lines:
        sys_mention_id, system_spans, system_attributes = parse_line(
            sl, eval_mode, invisible_ids)
        system_mention_table.append(
            (system_spans, system_attributes, sys_mention_id))
        all_possible_types.add(system_attributes[0])

    for gl in g_mention_lines:
        gold_mention_id, gold_spans, gold_attributes = parse_line(
            gl, eval_mode, invisible_ids)
        gold_mention_table.append((gold_spans, gold_attributes, gold_mention_id))
        all_possible_types.add(gold_attributes[0])

    # if mention_span_duplicate_with_same_type(system_mention_table):
    #     logger.error("Mentions with same type cannot have same span")
    #     terminate_with_error()

    # Store list of mappings with the score as a priority queue
    # score is stored using negative for easy sorting
    all_gold_system_mapping_scores = []

    print_score_matrix = False

    for system_index, (system_spans, system_attributes,
                       sys_mention_id) in enumerate(system_mention_table):
        if print_score_matrix:
            print system_index,
        for index, (gold_spans, gold_attributes, gold_mention_id) in enumerate(
                gold_mention_table):
            overlap = compute_overlap_score(gold_spans,
                                            system_spans, eval_mode)
            if len(gold_spans) == 0:
                logger.warning("Found empty gold standard at doc : %s" % doc_id)

            if print_score_matrix:
                print "%.1f" % overlap,

            if overlap > 0:
                # maintaining a max heap based on overlap score
                heapq.heappush(
                    all_gold_system_mapping_scores,
                    (-overlap, system_index, index))
        if print_score_matrix:
            print

    mapped_system_mentions = {}

    # a list system index and the mapping score for each gold
    gold_2_system_many_2_many_mapping = [[] for _ in xrange(len(g_mention_lines))]

    while len(all_gold_system_mapping_scores) != 0:
        neg_mapping_score, mapping_system_index, mapping_gold_index = \
            heapq.heappop(all_gold_system_mapping_scores)
        gold_2_system_many_2_many_mapping[mapping_gold_index].append((mapping_system_index, -neg_mapping_score))
        add_to_multi_map(mapped_system_mentions, mapping_system_index, mapping_gold_index)

    # list of possible gold mention that a system can map to, one at a time
    system_2_gold_one_2_one_mappings = generate_all_system_branches(mapped_system_mentions)

    # list of all possible mappings that satisfy the following:
    # 1. gold can mapped to multiple systems
    # 2. system can be mapped to only one gold
    all_possible_gold_2_system_one_2_many_mappings = []
    for system_2_gold_mapping in system_2_gold_one_2_one_mappings:
        all_possible_gold_2_system_one_2_many_mappings.append(
            unify_system_mapping(gold_2_system_many_2_many_mapping, system_2_gold_mapping))

    best_tp = 0
    best_attribute_based_tps = [0] * len(all_attribute_combinations)
    best_all_att_mapping = all_possible_gold_2_system_one_2_many_mappings[0]  # initialize with the first one

    for possible_gold_2_system_one_2_many_mapping in all_possible_gold_2_system_one_2_many_mappings:
        temp_tp, temp_abtps = get_tp(all_attribute_combinations, possible_gold_2_system_one_2_many_mapping,
                                     gold_mention_table, system_mention_table, doc_id)
        if temp_tp > best_tp:
            best_tp = temp_tp
        for att_comb_index, abtp in enumerate(temp_abtps):
            if abtp > best_attribute_based_tps[att_comb_index]:
                best_attribute_based_tps[att_comb_index] = abtp
                if att_comb_index == len(temp_abtps) - 1:
                    best_all_att_mapping = possible_gold_2_system_one_2_many_mapping

    if diff_out is not None:
        write_gold_and_system_mappings(doc_id, system_id, best_all_att_mapping, gold_mention_table,
                                       system_mention_table, diff_out)

    attribute_based_fps = [0.0] * len(all_attribute_combinations)
    for attribute_comb_index, abtp in enumerate(best_attribute_based_tps):
        attribute_based_fps[attribute_comb_index] = len(s_mention_lines) - abtp

    # unmapped system mentions and the partial scores are considered as false positive
    fp = len(s_mention_lines) - best_tp

    doc_scores.append((best_tp, fp, zip(best_attribute_based_tps, attribute_based_fps),
                       len(g_mention_lines), len(s_mention_lines), doc_id))

    gold_corefs = [coref for coref in [parse_relation(l) for l in g_relation_lines] if
                   coref[0] == coreference_relation_name]

    sys_corefs = [coref for coref in [parse_relation(l) for l in s_relation_lines] if
                  coref[0] == coreference_relation_name]

    if eval_coref:
        # all one to one mappings
        all_gold_2_system_one_2_one_mapping = generate_all_one_to_one_mapping(
            all_possible_gold_2_system_one_2_many_mappings)
        # prepare conll style coreference input
        conll_converter = ConllConverter(id2token_map, doc_id, gold_conll_file_out, sys_conll_file_out)
        conll_converter.prepare_conll_lines(gold_corefs, sys_corefs,
                                            gold_mention_table, system_mention_table,
                                            all_gold_2_system_one_2_one_mapping)
    return True


def get_num(x):
    return int(''.join(ele for ele in x if ele.isdigit()))


def natural_order(key):
    convert = lambda text: int(text) if text.isdigit() else text
    return [convert(c) for c in re.split('([0-9]+)', key)]


def transitive_not_resolved(clusters):
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


def add_to_multi_map(map, key, val):
    if key not in map:
        map[key] = []
    map[key].append(val)


def within_cluster_span_duplicate(cluster, event_mention_id_2_sorted_tokens):
    # print cluster
    # print event_mention_id_2_sorted_tokens
    span_map = {}
    for eid in cluster:
        span = tuple(event_mention_id_2_sorted_tokens[eid])
        if span in span_map:
            logger.error("Span within the same cluster cannot be the same.")
            logger.error("%s->[%s]" % (eid, ",".join(span)))
            logger.error("%s->[%s]" % (span_map[span], ",".join(span)))
            return True
        else:
            span_map[span] = eid


def generate_all_one_to_one_mapping(all_possible_gold_2_system_one_2_many_mappings):
    all_one_2_one_mapping = []
    for mapping in all_possible_gold_2_system_one_2_many_mappings:
        all_one_2_one_mapping

    return all_one_2_one_mapping


class ConllConverter:
    def __init__(self, id2token_map, doc_id, gold_conll_file_out, sys_conll_file_out):
        """
        :param id2token_map: a dict, map from token id to its string
        :param doc_id: the document id
        :param gold_conll_file_out
        :param sys_conll_file_out
        :return:
        """
        self.id2token = id2token_map
        self.doc_id = doc_id
        self.gold_conll_file_out = gold_conll_file_out
        self.sys_conll_file_out = sys_conll_file_out

    def prepare_conll_lines(self, gold_corefs, sys_corefs, gold_mention_table, system_mention_table,
                            all_gold_2_system_one_2_one_mapping):
        """
        Convert to ConLL style lines
        :param gold_corefs: gold coreference chain
        :param sys_corefs: system coreferenc chain
        :param gold_mention_table:  gold mention table
        :param system_mention_table: system mention table
        :param all_gold_2_system_one_2_one_mapping: all possible mapping between gold and system
        :return:
        """
        if not self.prepare_lines(gold_corefs, self.gold_conll_file_out, gold_mention_table):
            logger.error(
                "Gold standard has data problem for doc [%s], please refer to log. Quitting..."
                % self.doc_id)
            terminate_with_error()

        if not self.prepare_lines(sys_corefs, self.sys_conll_file_out, system_mention_table):
            logger.error(
                "System has data problem for doc [%s], please refer to log. Quitting..."
                % self.doc_id)
            terminate_with_error()

    def prepare_lines(self, corefs, out, mention_table):
        print mention_table
        sys.stdin.readline()

        clusters = {}
        for cluster_id, one_coref_cluster in enumerate(corefs):
            clusters[cluster_id] = set(one_coref_cluster[2])

        if transitive_not_resolved(clusters):
            return False

        # first extract the following mapping from the mention_table
        token2event = {}
        event_mention_id_2_sorted_tokens = {}

        singleton_cluster_id = len(corefs)
        for mention in mention_table:
            tokens = sorted(mention[0], key=natural_order)
            event_id = mention[2]

            non_singleton_cluster_id = None

            event_mention_id_2_sorted_tokens[event_id] = tokens

            for cluster_id, cluster_mentions in clusters.iteritems():
                if event_id in cluster_mentions:
                    non_singleton_cluster_id = cluster_id
                    break

            if non_singleton_cluster_id is not None:
                output_cluster_id = non_singleton_cluster_id
            else:
                output_cluster_id = singleton_cluster_id
                singleton_cluster_id += 1

            if len(tokens) == 1:
                add_to_multi_map(token2event, tokens[0], "(%s)" % output_cluster_id)
            else:
                add_to_multi_map(token2event, tokens[0], "(%s" % output_cluster_id)
                add_to_multi_map(token2event, tokens[-1], "%s)" % output_cluster_id)

        for cluster_id, cluster in clusters.iteritems():
            if within_cluster_span_duplicate(cluster, event_mention_id_2_sorted_tokens):
                return False

        out.write("%s (%s); part 000%s" % (conll_bod_marker, self.doc_id, os.linesep))
        for token_id, token in sorted(self.id2token.iteritems(), key=lambda key_value: natural_order(key_value[0])):
            coref_str = "|".join(token2event[token_id]) if token_id in token2event else "-"
            out.write("%s\t%s\t%s\t%s\n" % (self.doc_id, get_num(token_id), token, coref_str))
        out.write(conll_eod_marker + os.linesep)

        return True


if __name__ == "__main__":
    main()

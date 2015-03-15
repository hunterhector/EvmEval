#!/usr/bin/python

"""
    A simple scorer that reads the CMU Event Mention Detection Format
    data and produce a mention based F-Scores

    This scorer also require token files to conduct evaluation

    Author: Zhengzhong Liu ( liu@cs.cmu.edu )
"""
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

logger = logging.getLogger()
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s : %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

comment_marker = "#"
bod_marker = "#BeginOfDocument"  # mark begin of a document
eod_marker = "#EndOfDocument"  # mark end of a document

token_file_ext = ".txt.tab"
source_file_ext = ".tkn.txt"
visualization_path = "visualization"
visualization_json_data_subpath = "json"

# run this on an annotation to confirm
invisible_words = {'the', 'a', 'an', 'I', 'you', 'he', 'she', 'we', 'my',
                   'your', 'her', 'our', 'who', 'what', 'where', 'when'}

# attribute names
attribute_names = ["mention_type", "realis_status"]
all_attribute_combinations = []

gold_docs = {}
system_docs = {}
doc_ids_to_score = []
all_possible_types = set()
evaluating_index = 0
token_dir = "."
text_dir = "."

diff_out = None
eval_out = None

doc_scores = []

token_joiner = ","
span_seperator = ";"
span_joiner = "_"

token_offset_fields = [2, 3]

missingAttributePlaceholder = "NOT_ANNOTATED"


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
    global diff_out
    global eval_out
    global token_dir
    global token_file_ext
    global source_file_ext
    global visualization_path
    global text_dir
    global token_offset_fields
    global all_attribute_combinations

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
        "-o", "--output", help="Optional evaluation result redirects, it is suggested"
                               "to be sued when using visualization, otherwise the results will"
                               "be hard to read")
    parser.add_argument(
        "-t", "--token_path", help="Path to the directory containing the "
                                   "token mappings file", required=True)
    parser.add_argument(
        "-of", "--offset_field", help="A pair of integer indicates which column we should "
                                      "read the offset in the token mapping file, index starts"
                                      "at 0, default value will be %s" % token_offset_fields
    )
    parser.add_argument(
        "-te", "--token_table_extension",
        help="any extension appended after docid of token table files. "
             "Default is [%s]" % token_file_ext)
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
        eval_out = open(out_path, 'w')
        logger.info("Evaluation output will be saved at %s" % out_path)
    else:
        eval_out = sys.stdout
        logger.info("Evaluation output at standard out")

    if args.token_table_extension is not None:
        token_file_ext = args.token_table_extension

    if os.path.isfile(args.gold):
        gf = open(args.gold)
    else:
        logger.error("Cannot find gold standard file at " + args.gold)
        sys.exit(1)

    if os.path.isfile(args.system):
        sf = open(args.system)
    else:
        logger.error("Cannot find system file at " + args.system)
        sys.exit(1)

    if args.comparison_output is not None:
        diff_out_path = args.comparison_output
        create_parent_dir(diff_out_path)
        diff_out = open(diff_out_path, 'w')

    if args.token_path is not None:
        if os.path.isdir(args.token_path):
            logger.debug("Will search token files in " + args.token_path)
            token_dir = args.token_path
        else:
            logger.debug("Cannot find given token directory at [%s], "
                         "will try search for current directory" % args.token_path)

    if args.offset_field is not None:
        try:
            token_offset_fields = [int(x) for x in args.offset_field.split(",")]
        except ValueError as _:
            logger.error("Should provide two integer with comma in between")

    # token based eval mode
    eval_mode = EvalMethod.Token
    all_attribute_combinations = get_attr_combinations(attribute_names)
    read_all_doc(gf, sf)
    while True:
        if not evaluate(eval_mode):
            break
    print_eval_results()
    logger.info("Evaluation Done.")


def get_combined_attribute_header(all_comb, size):
    header_list = [pad_char_before_until("plain", size)]
    for comb in all_comb:
        # print comb
        attr_header = []
        for attr_pair in comb:
            attr_header.append(attr_pair[1])
        header_list.append(pad_char_before_until("+".join(attr_header), size))
    return header_list


def get_cell_width(doc_scores):
    max_doc_name = 0
    for info in doc_scores:
        docId = info[5]
        if len(docId) > max_doc_name:
            max_doc_name = len(docId)
    return max_doc_name


def pad_char_before_until(s, n, c=" "):
    return c * (n - len(s)) + s


def print_eval_results():
    total_gold_mentions = 0
    total_system_mentions = 0
    valid_docs = 0

    plain_global_scores = [0.0] * 4
    attribute_based_global_scores = [[0.0] * 4 for _ in xrange(len(all_attribute_combinations))]

    doc_id_width = get_cell_width(doc_scores)

    eval_out.write("========Document results==========\n")
    small_header_item = "Prec  \tRec  \tF1   "
    attribute_header_list = get_combined_attribute_header(all_attribute_combinations, len(small_header_item))
    small_headers = [small_header_item] * (len(all_attribute_combinations) + 1)
    eval_out.write(pad_char_before_until("", doc_id_width) + "\t" + "\t|\t".join(attribute_header_list) + "\n")
    eval_out.write(pad_char_before_until("Doc ID", doc_id_width) + "\t" + "\t|\t".join(small_headers) + "\n")

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
                attribute_based_global_scores[comb_index][score_index] += score

        eval_out.write(
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

    eval_out.write("\n=======Final Results=========\n")
    max_attribute_name_width = len(max(attribute_header_list, key=len))
    attributes_name_header = pad_char_before_until("Attributes", max_attribute_name_width)

    final_result_big_header = ["Micro Average", "Macro Average"]

    eval_out.write(
        pad_char_before_until("", max_attribute_name_width, " ") + "\t" + "\t".join(
            [pad_char_before_until(h, len(small_header_item)) for h in final_result_big_header]) + "\n")
    eval_out.write(attributes_name_header + "\t" + "\t".join([small_header_item] * 2) + "\n")
    eval_out.write(pad_char_before_until(attribute_header_list[0], max_attribute_name_width) + "\t" + "\t".join(
        "%.2f" % f for f in plain_average_scores) + "\n")
    for attr_index, attr_based_score in enumerate(attribute_based_global_scores):
        attr_average_scores = get_averages(attr_based_score, total_gold_mentions, total_system_mentions, valid_docs)
        eval_out.write(
            pad_char_before_until(attribute_header_list[attr_index + 1], max_attribute_name_width) + "\t" + "\t".join(
                "%.2f" % f for f in attr_average_scores) + "\n")

    if eval_out is not None:
        eval_out.flush()
        if not eval_out == sys.stdout:
            eval_out.close()

    if diff_out is not None:
        diff_out.close()


def get_averages(scores, num_gold, num_sys, num_docs):
    micro_prec = safe_div(scores[0], num_sys)
    micro_recall = safe_div(scores[0], num_gold)
    micro_f1 = f1(micro_prec, micro_recall)
    macro_prec = safe_div(scores[2], num_docs)
    macro_recall = safe_div(scores[3], num_docs)
    macro_f1 = f1(macro_prec, macro_recall)
    return micro_prec, micro_recall, micro_f1, macro_prec, macro_recall, macro_f1


def read_token_ids(g_file_name):
    invisible_ids = set()
    id2token_map = {}
    id2span_map = {}

    token_file_path = os.path.join(token_dir, g_file_name + token_file_ext)

    logger.debug("Reading token for " + g_file_name)

    try:
        token_file = open(token_file_path)

        # discard the header
        header = token_file.readline()

        for tline in token_file:
            fields = tline.rstrip().split("\t")
            if len(fields) < 4:
                logger.debug("Wierd token line " + tline)
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
        logger.debug(
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
        logger.debug("No document to score, file names are all different!")

    doc_ids_to_score = sorted(g_id_set)


def read_docs_with_doc_id(f):
    all_docs = {}
    lines = []
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
                all_docs[doc_id] = lines
                lines = []
        elif line == "":
            pass
        else:
            lines.append(line)

    return all_docs


def get_next_doc():
    global evaluating_index
    if evaluating_index < len(doc_ids_to_score):
        doc_id = doc_ids_to_score[evaluating_index]
        evaluating_index += 1
        if doc_id in system_docs:
            return True, gold_docs[doc_id], system_docs[doc_id], doc_id
        else:
            return True, gold_docs[doc_id], [], doc_id
    else:
        return False, [], [], "End_of_docs"


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
    if len(fields) != 6 + num_attributes and len(fields) != 5 + num_attributes:
        logger.error("Output are not correctly formatted")
    token_ids = parse_token_ids(fields[3], invisible_ids)

    return fields[2], token_ids, fields[5:5 + num_attributes]


def parse_line(l, eval_mode, invisible_ids):
    return parse_token_based_line(l, invisible_ids)


def validate_spans(spans):
    last_end = -1
    for span in spans:
        if len(span) == 2 and span[1] > span[0]:
            pass
        else:
            logger.error(span + " is not a valid span")
            sys.exit(1)
        if span[0] < last_end:
            logger.error("Spans cannot overlaps")
            sys.exit(1)


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


def read_original_text(doc_id):
    text_path = os.path.join(text_dir, doc_id + source_file_ext)
    if os.path.exists(text_path):
        f = open(os.path.join(text_dir, doc_id + source_file_ext))
        return f.read()
    else:
        logger.error("Cannot locate original text, please check parameters")
        sys.exit(1)


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


def write_diff(text):
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
                                   system_mention_table):
    schedule = prepare_write_schedule(gold_mention_table, system_mention_table, assigned_gold_2_system_mapping)
    write_diff(bod_marker + " " + doc_id + "\n")

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

        write_diff("%s\t%s\t|\t%s\t%s\n" % (system_id, gold_info, sys_info, score_str))

    write_diff(eod_marker + " " + "\n")


def evaluate(eval_mode):
    res, g_lines, s_lines, doc_id = get_next_doc()

    if not res:
        return False

    invisible_ids, id2token_map, id2span_map = read_token_ids(doc_id)

    system_id = ""
    if len(s_lines) > 0:
        fields = s_lines[0].split("\t")
        if len(fields) > 0:
            system_id = fields[0]

    # parse the lines in file
    system_mention_table = []
    gold_mention_table = []

    for sl in s_lines:
        sys_mention_id, system_spans, system_attributes = parse_line(
            sl, eval_mode, invisible_ids)
        system_mention_table.append(
            (system_spans, system_attributes, sys_mention_id))
        all_possible_types.add(system_attributes[0])

    for gl in g_lines:
        gold_mention_id, gold_spans, gold_attributes = parse_line(
            gl, eval_mode, invisible_ids)
        gold_mention_table.append((gold_spans, gold_attributes, gold_mention_id))
        all_possible_types.add(gold_attributes[0])

    # Store list of mappings with the score as a priority queue
    # score is stored using negative for easy sorting
    all_gold_system_mapping_scores = []

    for system_index, (system_spans,
                       system_attributes, sys_mention_id) in enumerate(
            system_mention_table):
        for index, (gold_spans, gold_attributes, gold_mention_id) in enumerate(
                gold_mention_table):
            overlap = compute_overlap_score(gold_spans,
                                            system_spans, eval_mode)
            if len(gold_spans) == 0:
                logger.warning("Found empty gold standard at doc : %s" % doc_id)

            if overlap > 0:
                # maintaining a max heap based on overlap score
                heapq.heappush(
                    all_gold_system_mapping_scores,
                    (-overlap, system_index, index))

    mapped_system_mentions = set()

    # a list system index and the mapping score for each gold
    assigned_gold_2_system_mapping = [[] for _ in xrange(len(g_lines))]

    # greedily matching gold and system by selecting the highest score first
    # one system mention can be mapped to only one gold
    while len(all_gold_system_mapping_scores) != 0:
        neg_mapping_score, mapping_system_index, mapping_gold_index = \
            heapq.heappop(all_gold_system_mapping_scores)
        if mapping_system_index not in mapped_system_mentions:
            assigned_gold_2_system_mapping[mapping_gold_index].append((mapping_system_index, -neg_mapping_score))
        mapped_system_mentions.add(mapping_system_index)

    tp = 0.0
    fp = 0.0
    plain_gold_found = 0.0

    attribute_based_tps = [0.0] * len(all_attribute_combinations)
    attribute_based_gold_counts = [0.0] * len(all_attribute_combinations)

    for gold_index, mapped_system_indices_and_scores in enumerate(
            assigned_gold_2_system_mapping):
        if len(mapped_system_indices_and_scores) > 0:
            plain_gold_found += 1
        else:
            continue

        max_mapping_score = mapped_system_indices_and_scores[0][1]
        tp += max_mapping_score

        gold_attrs = gold_mention_table[gold_index][1]

        for attr_comb_index, attr_comb in enumerate(all_attribute_combinations):
            for system_index, score in mapped_system_indices_and_scores:
                system_attrs = system_mention_table[system_index][1]
                if attribute_based_match(attr_comb, gold_attrs, system_attrs, doc_id):
                    attribute_based_tps[attr_comb_index] += score
                    attribute_based_gold_counts[attr_comb_index] += 1.0
                    break

    write_gold_and_system_mappings(doc_id, system_id, assigned_gold_2_system_mapping, gold_mention_table,
                                   system_mention_table)

    attribute_based_fps = [0.0] * len(all_attribute_combinations)
    for attribute_comb_index, (abtp, abgc) in enumerate(zip(attribute_based_tps, attribute_based_gold_counts)):
        attribute_based_fps[attribute_comb_index] = len(s_lines) - abtp

    # unmapped system mentions are considered as false positive
    fp += len(s_lines) - plain_gold_found
    doc_scores.append((tp, fp, zip(attribute_based_tps, attribute_based_fps),
                       len(g_lines), len(s_lines), doc_id))

    return True


if __name__ == "__main__":
    main()
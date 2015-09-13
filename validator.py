#!/usr/bin/python

"""
    A simple validator that check whether the format can at be parsed by the scorer
    It might not be able to detect all the problems so please double-check the results
    carefully.

    Author: Zhengzhong Liu ( liu@cs.cmu.edu )
"""

import argparse
import logging
import sys
import os
import re

logger = logging.getLogger()

comment_marker = "#"
bod_marker = "#BeginOfDocument"  # mark begin of a document
eod_marker = "#EndOfDocument"  # mark end of a document
relation_marker = "@"  # mark start of a relation
coreference_relation_name = "Coreference"  # mark coreference

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
doc_ids_to_score = []
all_possible_types = set()
evaluating_index = 0

token_joiner = ","
span_seperator = ";"
span_joiner = "_"

missingAttributePlaceholder = "NOT_ANNOTATED"

total_mentions = 0

unrecognized_relation_count = 0
total_tokens_not_found = 0


class EvalMethod:
    Token, Char = range(2)


def exit_on_fail():
    logger.error("Validation failed.")
    logger.error("Please fix the warnings/errors.")
    sys.exit(255)


def main():
    parser = argparse.ArgumentParser(
        description="Validator to see if it can pass the scorer successfully")
    parser.add_argument("-s", "--system", help="System output", required=True)
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
    validator_log = os.path.basename(args.system) + ".errlog"
    handler = logging.FileHandler(validator_log)
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s : %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if os.path.isfile(args.system):
        sf = open(args.system)
    else:
        logger.error("Cannot find system file at " + args.system)
        exit_on_fail()

    if args.debug:
        handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)

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
    if not read_all_doc(sf):
        exit_on_fail()

    validation_success = True
    while has_next_doc():
        if not validate_next(eval_mode, token_dir, token_offset_fields, args.token_table_extension):
            validation_success = False
            break

    logger.info("Submission contains %d files, %d mentions" % (len(gold_docs), total_mentions))

    if not validation_success:
        exit_on_fail()
    else:
        logger.info("Validation did not find obvious errors.")

    logger.info("Validation Finished.")


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
                logger.error("Token line should have 4 fields, found the following : ")
                logger.error(tline)
                continue

            token = fields[1].lower().strip().rstrip()
            token_id = fields[0]
            id2token_map[token_id] = token

            try:
                token_span = (int(fields[token_offset_fields[0]]), int(fields[token_offset_fields[1]]))
                id2span_map[token_id] = token_span
            except ValueError as e:
                logger.error("Cannot find field %s and %s in token file %s in the following line: " % (
                    token_offset_fields[0], token_offset_fields[1], token_file))
                logger.error(tline)
            if token in invisible_words:
                invisible_ids.add(token_id)
    except IOError:
        logger.error("Cannot find token file for doc [%s] at [%s], did you use correct file paths?" % (
            g_file_name, token_file_path))
        pass
    return invisible_ids, id2token_map, id2span_map


def read_all_doc(gf):
    global gold_docs
    global doc_ids_to_score
    gold_docs = read_docs_with_doc_id(gf)
    if "" in gold_docs:
        gold_docs.pop("")
    g_doc_ids = gold_docs.keys()
    g_id_set = set(g_doc_ids)

    doc_ids_to_score = sorted(g_id_set)

    if len(g_doc_ids) == 0:
        logger.error("No document id found for [%s], please check begin and end marker.")
        return False
    return True


def check_unique(keys):
    return len(keys) == len(set(keys))


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
        return True, gold_docs[doc_id], ([], []), doc_id
    else:
        logger.error("Reaching end of all documents")
        return False, ([], []), ([], []), "End_Of_Documents"


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
    min_len = len(attribute_names) + 5
    if len(fields) < min_len:
        logger.error(
            "System line too few fields, there should be at least %d, found %d. Incorrect lines are logged below:" % (
                min_len, len(fields)))
        logger.error(l)
        logger.error(fields)
        exit_on_fail()
    token_ids = parse_token_ids(fields[3], invisible_ids)

    return fields[2], token_ids, fields[5:]


def parse_line(l, eval_mode, invisible_ids):
    return parse_token_based_line(l, invisible_ids)


def parse_relation(relation_line):
    parts = relation_line.split("\t")
    if len(parts) < 3:
        logger.error("Relation should have at least 3 fields, found the following:")
        logger.error(parts)
        exit_on_fail()
    relation_arguments = parts[2].split(",")
    return parts[0], parts[1], relation_arguments


def natural_order(key):
    convert = lambda text: int(text) if text.isdigit() else text
    return [convert(c) for c in re.split('([0-9]+)', key)]


def get_eid_2_sorted_token_map(mention_table):
    event_mention_id_2_sorted_tokens = {}
    for mention in mention_table:
        tokens = sorted(mention[0], key=natural_order)
        event_id = mention[2]
        event_mention_id_2_sorted_tokens[event_id] = tokens
    return event_mention_id_2_sorted_tokens


def validate_next(eval_mode, token_dir, token_offset_fields, token_file_ext):
    global total_mentions
    global unrecognized_relation_count

    res, (g_mention_lines, g_relation_lines), (s_mention_lines, s_relation_lines), doc_id = get_next_doc()

    invisible_ids, id2token_map, id2span_map = read_token_ids(token_dir, doc_id, token_file_ext, token_offset_fields)

    # parse the lines in file
    gold_mention_table = []

    mention_ids = []
    for gl in g_mention_lines:
        gold_mention_id, gold_spans, gold_attributes = parse_line(
            gl, eval_mode, invisible_ids)
        gold_mention_table.append((gold_spans, gold_attributes, gold_mention_id))
        mention_ids.append(gold_mention_id)
        all_possible_types.add(gold_attributes[0])

    total_mentions += len(gold_mention_table)

    if not check_unique(mention_ids):
        logger.error("Duplicated mention id for doc %s" % doc_id)
        return False

    if has_invented_token(id2token_map, gold_mention_table):
        logger.error("Invented token id was found for doc %s" % doc_id)
        logger.error("Tokens not in tbf not found in token map : %d" % total_tokens_not_found)
        return False

    clusters = {}
    cluster_id = 0
    for l in g_relation_lines:
        relation = parse_relation(l)
        if relation[0] == coreference_relation_name:
            clusters[cluster_id] = set(relation[2])
            cluster_id += 1
        else:
            unrecognized_relation_count += 1
            logger.warning("Relation [%s] is not recognized, this task only takes [%s]", relation[0],
                           coreference_relation_name)

    if unrecognized_relation_count > 10:
        logger.error("Too many unrecognized relations : %d" % unrecognized_relation_count)
        return False

    if transitive_not_resolved(clusters):
        logger.error("Coreference transitive closure is not resolved! Please resolve before submitting.")
        logger.error("Problem was found in file %s" % doc_id)
        return False

    event_mention_id_2_sorted_tokens = get_eid_2_sorted_token_map(gold_mention_table)

    for cluster_id, cluster in clusters.iteritems():
        if invented_mention_check(cluster, event_mention_id_2_sorted_tokens):
            logger.error("Found invented id in clusters at doc [%s]" % doc_id)
            return False

        if within_cluster_span_duplicate(cluster, event_mention_id_2_sorted_tokens):
            logger.error("Please remove span duplicates before submitting")
            logger.error("Problem was found in file %s" % doc_id)
            return False

    return True


def has_invented_token(id2token_map, gold_mention_table):
    for gold_mention in gold_mention_table:
        spans = gold_mention[0]
        for tid in spans:
            if tid not in id2token_map:
                logger.error("Token Id [%s] is not in the given token map" % tid)
                return True
    return False


def invented_mention_check(cluster, event_mention_id_2_sorted_tokens):
    for eid in cluster:
        if not eid in event_mention_id_2_sorted_tokens:
            logger.error("Cluster contains ID not in event mention list [%s]" % eid)
            return True
        else:
            return False


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


def transitive_not_resolved(clusters):
    ids = clusters.keys()
    for i in range(0, len(ids) - 1):
        for j in range(i + 1, len(ids)):
            if len(clusters[i].intersection(clusters[j])) != 0:
                logger.error("Non empty intersection between clusters found.")
                logger.error(clusters[i])
                logger.error(clusters[j])
                return True
    return False


if __name__ == "__main__":
    main()

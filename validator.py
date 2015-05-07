#!/usr/bin/python

"""
    A validator that check whether the format can be parsed by the scorer

    Author: Zhengzhong Liu ( liu@cs.cmu.edu )
"""

# TODO add more informative tips about what goes wrong

import errno
import argparse
import logging
import sys
import os
import heapq
import itertools
import re

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

conll_bod_marker = "#begin document"
conll_eod_marker = "#end document"

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

eval_coref = True

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
    global coref_out
    global gold_conll_file_out
    global sys_conll_file_out
    global diff_out
    global eval_coref
    global mention_eval_out
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
    parser.add_argument("-s", "--system", help="System output", required=True)
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

    if args.token_table_extension is not None:
        token_file_ext = args.token_table_extension

    if os.path.isfile(args.system):
        gf = open(args.system)
        sf = open(args.system)
    else:
        logger.error("Cannot find system file at " + args.system)
        sys.exit(1)

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

    logger.info("Validation Done.")


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
    if len(fields) != 6 + num_attributes and len(fields) != 5 + num_attributes:
        logger.error("Output are not correctly formatted")
    token_ids = parse_token_ids(fields[3], invisible_ids)

    return fields[2], token_ids, fields[5:5 + num_attributes]


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


def evaluate(eval_mode):
    if has_next_doc():
        res, (g_mention_lines, g_relation_lines), (s_mention_lines, s_relation_lines), doc_id = get_next_doc()
    else:
        return False

    invisible_ids, id2token_map, id2span_map = read_token_ids(doc_id)

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

    # Store list of mappings with the score as a priority queue
    # score is stored using negative for easy sorting
    all_gold_system_mapping_scores = []

    for system_index, (system_spans, system_attributes,
                       sys_mention_id) in enumerate(system_mention_table):
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
    assigned_gold_2_system_mapping = [[] for _ in xrange(len(g_mention_lines))]

    # greedily matching gold and system by selecting the highest score first
    # one system mention can be mapped to only one gold
    while len(all_gold_system_mapping_scores) != 0:
        neg_mapping_score, mapping_system_index, mapping_gold_index = \
            heapq.heappop(all_gold_system_mapping_scores)
        if mapping_system_index not in mapped_system_mentions:
            assigned_gold_2_system_mapping[mapping_gold_index].append((mapping_system_index, -neg_mapping_score))
        mapped_system_mentions.add(mapping_system_index)

    tp = 0.0
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

    attribute_based_fps = [0.0] * len(all_attribute_combinations)
    for attribute_comb_index, (abtp, abgc) in enumerate(zip(attribute_based_tps, attribute_based_gold_counts)):
        attribute_based_fps[attribute_comb_index] = len(s_mention_lines) - abtp

    gold_corefs = [coref for coref in [parse_relation(l) for l in g_relation_lines] if
                   coref[0] == coreference_relation_name]

    sys_corefs = [coref for coref in [parse_relation(l) for l in s_relation_lines] if
                  coref[0] == coreference_relation_name]

    if eval_coref:
        # prepare conll style coreference input
        conll_converter = ConllConverter(id2token_map, doc_id)
        conll_converter.prepare_conll_lines(gold_corefs, sys_corefs, gold_mention_table, system_mention_table)
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
                logger.error("Non empty intersection between clusters found.")
                logger.error(clusters[i])
                logger.error(clusters[j])
                return True
    return False


def add_to_multi_map(map, key, val):
    if key not in map:
        map[key] = []
    map[key].append(val)


class ConllConverter:
    def __init__(self, id2token_map, doc_id):
        """
        :param id2token_map: a dict, map from token id to its string
        :param id2span_map: a dict, map from token id to its character span
        :param doc_id: the document id
        :return:
        """
        self.id2token = id2token_map
        self.doc_id = doc_id

    def prepare_conll_lines(self, gold_corefs, sys_corefs, gold_mention_table, system_mention_table):
        if not self.prepare_lines(gold_corefs, gold_mention_table):
            logger.error(
                "Gold standard has not resolved transitive closure of coreference for doc [%s], quitting..." % self.doc_id)
            exit(1)

        if not self.prepare_lines(sys_corefs, system_mention_table):
            logger.error(
                "System has not resolved transitive closure for coreference for doc [%s], quitting..." % self.doc_id)
            exit(1)

    def prepare_lines(self, corefs, mention_table):
        clusters = {}
        for cluster_id, gold_coref in enumerate(corefs):
            clusters[cluster_id] = set(gold_coref[2])

        if transitive_not_resolved(clusters):
            return False

        token2event = {}

        singleton_cluster_id = len(corefs)
        for mention in mention_table:
            tokens = sorted(mention[0], key=natural_order)
            event_id = mention[2]

            non_singleton_cluster_id = None

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

        return True


if __name__ == "__main__":
    main()
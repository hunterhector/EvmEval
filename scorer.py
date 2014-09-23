#!/usr/bin/python

"""
    A simple scorer that reads the CMU Event Mention Detection Format
    data and produce a mention based F-Scores

    This scorer needs will require token files as well to conduct evaluation
"""
import math
import errno
import argparse
import logging
import sys
import os
import heapq

comment_marker = "#"
bod_marker = "#BeginOfDocument"  # mark begin of a document
eod_marker = "#EndOfDocument"  # mark end of a document

logger = logging.getLogger()
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

# run this on an annotation to confirm
invisible_words = {'the', 'a', 'an', 'I', 'you', 'he', 'she', 'we', 'my',
                   'your', 'her', 'our', 'who', 'what', 'where', 'when'}

gold_docs = {}
system_docs = {}
doc_ids_to_score = []
evaluating_index = 0
token_dir = "."

diff_out = None
eval_out = None

docScores = []

token_joiner = ","
tokenFileExt = "tab"

span_seperator = ";"
span_joiner = "_"


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

    parser = argparse.ArgumentParser(
        description="Event mention scorer, which conducts token based "
                    "scoring, system and gold standard files should follows "
                    "the token-based format.")
    parser.add_argument("-g", "--gold", help="Golden Standard", required=True)
    parser.add_argument("-s", "--system", help="System output", required=True)
    parser.add_argument("-d", "--comparisonOutput",
                        help="Compare and help show the difference between "
                             "system and gold", required=True)
    parser.add_argument(
        "-o", "--output", help="Optional evaluation result redirects")
    parser.add_argument(
        "-t", "--tokenPath", help="Path to the directory containing the "
                                  "token mappings file", required=True)
    parser.add_argument(
        "-w", "--overwrite", help="force overwrite existing comparison "
                                  "file", action='store_true')
    parser.add_argument(
        "-b", "--debug", help="turn debug mode on", action="store_true")
    parser.set_defaults(debug=False)
    args = parser.parse_args()

    if args.output is not None:
        out_path = args.output
        create_parent_dir(out_path)
        eval_out = open(out_path, 'w')
    else:
        eval_out = sys.stdout

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

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

    if args.comparisonOutput is not None:
        diff_out_path = args.comparisonOutput
    else:
        logger.error("Comparison output not specified")
        sys.exit(1)

    create_parent_dir(diff_out_path)

    if not args.overwrite and os.path.isfile(diff_out_path):
        sys.stderr.write(
            "Output path for comparison [%s] already exists, use '-w' flag "
            "to force overwrite\n" % diff_out_path)
        sys.exit(1)

    diff_out = open(diff_out_path, 'w')

    if args.tokenPath is not None:
        if os.path.isdir(args.tokenPath):
            logger.debug("Will search token files in " + args.tokenPath)
            token_dir = args.tokenPath
        else:
            logger.debug("Cannot find given token directory at " +
                         args.tokenPath +
                         ", will try search for currrent directory")

    # token based eval mode
    eval_mode = EvalMethod.Token

    read_all_doc(gf, sf)

    # charactoer mode is disabled
    # if args.charMode:
    # eval_mode = EvalMethod.Char
    # logger.debug("NOTE: Using character based evaluation")

    while True:
        if not evaluate(eval_mode):
            break

    total_tp = 0
    total_fp = 0
    total_realis_correct = 0
    total_type_correct = 0
    total_gold_mentions = 0
    total_prec = 0
    total_recall = 0
    total_realis_accuracy = 0
    total_type_accuracy = 0
    valid_docs = 0

    eval_out.write("========Document results==========\n")
    for (tp, fp, typeCorrect, realisCorrect, goldMentions, docId) in docScores:
        prec = tp / (tp + fp) if tp + fp > 0 else float('nan')
        recall = tp / goldMentions if goldMentions > 0 else float('nan')
        doc_f1 = (2 * prec * recall / (prec + recall) if
                  prec + recall > 0 else float('nan'))
        type_accuracy = typeCorrect / goldMentions
        realis_accuracy = realisCorrect / goldMentions
        eval_out.write(
            "TP\tFP\t#Gold\tPrec\tRecall\tF1\tType\tRealis\tDoc Id\n")
        eval_out.write(
            "%.2f\t%.2f\t%d\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%s\n" % (
                tp, fp, goldMentions, prec, recall,
                doc_f1, type_accuracy, realis_accuracy, docId))

        if math.isnan(prec) or math.isnan(recall):
            # no mentions annotated, treat as invalid file
            pass
        else:
            valid_docs += 1
            total_tp += tp
            total_fp += fp
            total_gold_mentions += goldMentions
            total_prec += prec
            total_recall += recall
            total_realis_accuracy += realis_accuracy
            total_type_accuracy += type_accuracy
            total_realis_correct += realisCorrect
            total_type_correct += typeCorrect

    eval_out.write("\n=======Final Results=========\n")
    micro_prec = (total_tp / (total_tp + total_fp) if
                  total_tp + total_fp > 0 else float('nan'))
    micro_recall = (total_tp / total_gold_mentions if
                    total_gold_mentions > 0 else float('nan'))
    micro_f1 = (2 * micro_prec * micro_recall / (micro_prec + micro_recall) if
                micro_prec + micro_recall > 0 else float('nan'))
    micro_type_accuracy = (total_type_correct / total_gold_mentions if
                           total_gold_mentions > 0 else float('nan'))
    micro_realis_accuracy = (total_realis_correct / total_gold_mentions if
                             total_gold_mentions > 0 else float('nan'))

    macro_prec = total_prec / valid_docs if valid_docs > 0 else float('nan')
    macro_recall = (total_recall / valid_docs if
                    valid_docs > 0 else float('nan'))
    macro_f1 = (2 * macro_prec * macro_recall / (macro_prec + macro_recall) if
                macro_prec + macro_recall > 0 else float('nan'))
    macro_type_accuracy = (total_type_accuracy / valid_docs if
                           valid_docs > 0 else float('nan'))
    macro_realis_accuracy = (total_realis_accuracy / valid_docs if
                             valid_docs > 0 else float('nan'))

    eval_out.write("Precision (Micro Average): %.4f\n" % micro_prec)
    eval_out.write("Recall (Micro Average):%.4f\n" % micro_recall)
    eval_out.write("F1 (Micro Average):%.4f\n" % micro_f1)
    eval_out.write(
        "Mention type detection accuracy (Micro Average):%.4f\n" %
        micro_type_accuracy)
    eval_out.write(
        "Mention realis status accuracy (Micro Average):%.4f\n" %
        micro_realis_accuracy)

    eval_out.write("Precision (Macro Average): %.4f\n" % macro_prec)
    eval_out.write("Recall (Macro Average): %.4f\n" % macro_recall)
    eval_out.write("F1 (Macro Average): %.4f\n" % macro_f1)
    eval_out.write(
        "Mention type detection accuracy (Macro Average):%.4f\n" %
        macro_type_accuracy)
    eval_out.write(
        "Mention realis status accuracy (Macro Average):%.4f\n" %
        macro_realis_accuracy)

    if eval_out is not None:
        eval_out.close()
    diff_out.close()


def get_invisible_word_ids(g_file_name):
    invisible_ids = set()

    token_file_path = os.path.join(token_dir, g_file_name + "." + tokenFileExt)

    try:
        token_file = open(token_file_path)

        # discard the header
        header = token_file.readline()

        for tline in token_file:
            fields = tline.rstrip().split("\t")
            if len(fields) != 6:
                logger.debug("Wierd token line " + tline)
                continue
            if fields[1].lower().strip().rstrip() in invisible_words:
                invisible_ids.add(fields[0])

    except IOError:
        logger.debug(
            "Cannot find token file for doc [%s], "
            "will use empty invisible words list" % g_file_name)
        pass

    return invisible_ids


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
        logger.warning("The following document are not found in system")
        for d in g_minus_s:
            logger.warning("\t- " + d)

    if len(s_minus_g) > 0:
        logger.warning("The following document are not found in gold standard")
        for d in s_minus_g:
            logger.warning("\t- " + d)

    doc_ids_to_score = sorted(common_id_set)


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
        return True, gold_docs[doc_id], system_docs[doc_id], doc_id
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
            logger.debug("Token Id %d is filtered" % token_id)
            pass
    return filtered_token_ids


def parse_char_based_line(l):
    """
    Method to parse the character based line, which does not support
    removal of invisible words
    """
    fields = l.split("\t")
    if len(fields) != 8:
        logger.error("Output are not correctly formatted")
    spans = parse_spans(fields[3])
    mention_type = fields[5]
    realis_status = fields[6]
    return spans, mention_type, realis_status


def parse_token_based_line(l, invisible_ids):
    """
    parse the line, get the token ids, remove invisible ones
    """
    fields = l.split("\t")
    if len(fields) != 8:
        logger.error("Output are not correctly formatted")
    token_ids = parse_token_ids(fields[3], invisible_ids)
    mention_type = fields[5]
    realis_status = fields[6]
    return token_ids, mention_type, realis_status


def parse_line(l, eval_mode, invisible_ids):
    if eval_mode == EvalMethod.Token:
        return parse_token_based_line(l, invisible_ids)
    else:
        return parse_char_based_line(l)


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


def compute_char_overlap_score(g_spans, s_spans):
    """
    character based overlap score
    """
    # validate system span
    validate_spans(s_spans)

    g_length = 0
    for s in g_spans:
        g_length += (s[1] - s[0])

    slength = 0
    for s in s_spans:
        slength += (s[1] - s[0])

    total_overlap = 0.0
    for gSpan in g_spans:
        for sSpan in s_spans:
            total_overlap += span_overlap(gSpan, sSpan)

    # choose to use the longer length
    deno = g_length if g_length < slength else slength

    return total_overlap / deno


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
    if eval_mode == EvalMethod.Token:
        return compute_token_overlap_score(system_outputs, gold_annos)
    else:
        return compute_char_overlap_score(system_outputs, gold_annos)


def evaluate(eval_mode):
    res, g_lines, s_lines, doc_id = get_next_doc()

    if not res:
        return False

    invisible_ids = get_invisible_word_ids(doc_id) \
        if eval_mode == EvalMethod.Token else set()

    system_id = ""
    if len(s_lines) > 0:
        fields = s_lines[0].split("\t")
        if len(fields) > 0:
            system_id = fields[0]

    # parse the lines in file
    system_mention_table = []
    gold_mention_table = []

    for sl in s_lines:
        system_outputs, system_mention_type, system_realis = parse_line(
            sl, eval_mode, invisible_ids)
        system_mention_table.append(
            (system_outputs, system_mention_type, system_realis))

    for gl in g_lines:
        gold_annos, gold_mention_type, gold_realis = parse_line(
            gl, eval_mode, invisible_ids)
        gold_mention_table.append((gold_annos, gold_mention_type, gold_realis))

    # Store list of mappings with the score as a priority queue
    all_gold_system_mapping_scores = []

    # first item in the list store list of system mentions that mapped to
    # it, second item is the overlap score (negated for easy sorting)
    assigned_gold_2_system_mapping = [([], -1)] * len(g_lines)

    for system_index, (system_outputs,
                       system_mention_type, system_realis) in enumerate(
            system_mention_table):
        # largestOverlap = -1.0
        # corresIndex = -1

        for index, (gold_annos, gold_mention_type, gold_realis) in enumerate(
                gold_mention_table):
            overlap = compute_overlap_score(gold_annos,
                                            system_outputs, eval_mode)
            if len(gold_annos) == 0:
                logger.debug("Found empty gold standard")

            if overlap > 0:
                # maintaining a max heap based on overlap score
                heapq.heappush(
                    all_gold_system_mapping_scores,
                    (-overlap, system_index, index))

    mapped_system_mentions = set()
    num_gold_found = 0

    while len(all_gold_system_mapping_scores) != 0:
        neg_mapping_score, mapping_system_index, mapping_gold_index = \
            heapq.heappop(all_gold_system_mapping_scores)
        if mapping_system_index not in mapped_system_mentions:
            if assigned_gold_2_system_mapping[mapping_gold_index][1] == -1:
                assigned_gold_2_system_mapping[mapping_gold_index] = (
                    [mapping_system_index], -neg_mapping_score)
                num_gold_found += 1
            else:
                assigned_gold_2_system_mapping[mapping_gold_index][
                    0].append(mapping_system_index)

            mapped_system_mentions.add(mapping_system_index)

    tp = 0.0
    fp = 0.0
    type_correct = 0.0
    realis_correct = 0.0

    for gold_index, (system_indices, score) in enumerate(
            assigned_gold_2_system_mapping):
        if score > 0:  # -1 indicates no mapping
            tp += score
            portion_score = 1.0 / len(system_indices)

            for system_index in system_indices:
                if (system_mention_table[system_index][2] ==
                        gold_mention_table[gold_index][2]):
                    realis_correct += portion_score

                if (system_mention_table[system_index][1] ==
                        gold_mention_table[gold_index][1]):
                    type_correct += portion_score

    diff_out.write(bod_marker + " " + doc_id + "\n")
    for gIndex, gLine in enumerate(g_lines):
        gold_content = gLine.split("\t", 1)
        system_index, mapping_score = assigned_gold_2_system_mapping[gIndex]
        score_out = "%.4f" % mapping_score if mapping_score != -1 else "-"
        diff_out.write("%s\t%s\t%s\n" %
                       (system_id, gold_content[1], score_out))
    diff_out.write(eod_marker + " " + "\n")

    # unmapped system mentions are considered as false positive
    fp += len(s_lines) - num_gold_found

    docScores.append((tp, fp, type_correct, realis_correct,
                      len(g_lines), doc_id))
    return True


if __name__ == "__main__":
    main()

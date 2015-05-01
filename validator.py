#!/usr/bin/python

"""
    A validator that check whether the format can be parsed by the scorer

    Author: Zhengzhong Liu ( liu@cs.cmu.edu )
"""
import errno
import argparse
import logging
import sys
import os

# TODO validator should share the parsing code with scorer
comment_marker = "#"
bod_marker = "#BeginOfDocument"  # mark begin of a document
eod_marker = "#EndOfDocument"  # mark end of a document
relation_marker = "@"   # mark relation

logger = logging.getLogger()
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

# run this on an annotation to confirm
invisible_words = {'the', 'a', 'an', 'I', 'you', 'he', 'she', 'we', 'my',
                   'your', 'her', 'our', 'who', 'what', 'where', 'when'}

system_docs = {}
doc_ids_to_score = []
evaluating_index = 0
token_dir = "."

token_joiner = ","
token_file_ext = ".txt.tab"

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
    global token_file_ext

    parser = argparse.ArgumentParser(
        description="Validates the system output.")
    parser.add_argument("-s", "--system", help="System output", required=True)
    parser.add_argument(
        "-t", "--tokenPath", help="Path to the directory containing the "
                                  "token mappings file", required=True)
    parser.add_argument(
        "-te", "--token_table_extension",
        help="any extension appended after docid of token table files. "
             "Default is " + token_file_ext)

    args = parser.parse_args()

    if args.tokenPath is not None:
        if os.path.isdir(args.tokenPath):
            logger.debug("Will search token files in " + args.tokenPath)
            token_dir = args.tokenPath
        else:
            logger.debug("Cannot find given token directory at " +
                         args.tokenPath +
                         ", will try search for currrent directory")

    if os.path.isfile(args.system):
        sf = open(args.system)
    else:
        logger.error("Cannot find system file at " + args.system)
        sys.exit(1)

    read_all_doc(sf)

    eval_fail = False
    while True:
        res, s_lines, doc_id = get_next_doc()

        if not res:
            break

        if not validate(s_lines, doc_id):
            logger.error("Validation failed, please check data format")
            eval_fail = True
            break

    if not eval_fail:
        logger.warning("Syntax validation passed, please still check for system results carefully")


def get_invisible_word_ids(g_file_name):
    invisible_ids = set()

    token_file_path = os.path.join(token_dir, g_file_name + token_file_ext)

    try:
        token_file = open(token_file_path)

        # discard the header
        header = token_file.readline()

        for tline in token_file:
            fields = tline.rstrip().split("\t")
            if len(fields) < 4:
                logger.error("Error with token files, token line should have 4 fields")
                logger.error(tline)
                return False
            if fields[1].lower().strip().rstrip() in invisible_words:
                invisible_ids.add(fields[0])

    except IOError:
        logger.error(
            "Cannot find token file for doc [%s] at [%s], "
            "please check whether the token file exists" % (g_file_name, token_file_path))
        return False

    return invisible_ids


def read_all_doc(sf):
    global system_docs
    global doc_ids_to_score
    system_docs = read_docs_with_doc_id(sf)
    s_doc_ids = system_docs.keys()
    doc_ids_to_score = sorted(s_doc_ids)


def read_docs_with_doc_id(f):
    all_docs = {}

    lines = []
    doc_id = ""

    while True:
        line = f.readline()
        if not line:
            break
        line = line.strip()

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
        return True, system_docs[doc_id], doc_id
    else:
        return False, [], "End_of_docs"


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


def validate(s_lines, doc_id):
    invisible_ids = get_invisible_word_ids(doc_id)

    if not invisible_ids:
        return False

    for idx, l in enumerate(s_lines):
        fields = l.split("\t")
        if len(fields) != 8:
            logger.error("Output line [%d] on doc [%s] is not correctly formatted, "
                         "there should be 8 fields" % (idx, doc_id))
            return False

        local_doc_id = fields[1]
        if local_doc_id != doc_id:
            logger.error("Output line [%d] on doc [%s] with a different doc ID: [%s]" % (idx, doc_id, local_doc_id))
            return False

        token_ids = parse_token_ids(fields[3], invisible_ids)
        mention_type = fields[5]
        realis_status = fields[6]

    return True


if __name__ == "__main__":
    main()
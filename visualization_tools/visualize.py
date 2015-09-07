#!/usr/bin/python
# coding=utf-8

"""
    Used together with the scorer, produce a HTML page showing the difference
    between System and Gold Standard annotation.

    Visualization is done via embedded Brat tool

    Author: Zhengzhong Liu ( liu@cs.cmu.edu )
"""

import json
import SimpleHTTPServer
import SocketServer
import os
import sys
import argparse
import logging
import re

PORT = 8000

log_path = "server_log"
basic_event_color = "lightgreen"
missing_event_color = "#ffccaa"
partial_matched_event_color = "#aea0d6"
wrong_status_event_color = "#1E90FF"
missing_event_suffix = "_miss"
partial_matched_suffix = "_part"
wrong_status_suffix = "_wrong_status"
realis_mismatch_attr = "realis_wrong"
type_mismatch_attr = "type_wrong"

token_file_ext = ".tab"
source_file_ext = ".txt"
visualization_path = "visualization"
visualization_json_data_subpath = "json"
config_subpath = "config"
span_subpath = "span"

token_offset_fields = [2, 3]

comment_marker = "#"
bod_marker = "#BeginOfDocument"  # mark begin of a document
eod_marker = "#EndOfDocument"  # mark end of a document

token_joiner = ","

token_dir = "."
text_dir = "."

doc_ids_to_score = []
all_possible_mention_types = set()
all_possible_realis_types = set()

logger = logging.getLogger()
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s : %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)


def main():
    global token_file_ext
    global source_file_ext
    global visualization_path
    global visualization_json_data_subpath
    global token_offset_fields
    global text_dir
    global token_dir

    parser = argparse.ArgumentParser(
        description="Mention visualizer, will create a side-by-side embedded "
                    "visualization from the mapping "
    )
    parser.add_argument("-d", "--comparison_output",
                        help="The comparison output file between system and gold,"
                             " used to recover the mapping", required=True)
    parser.add_argument(
        "-t", "--tokenPath", help="Path to the directory containing the "
                                  "token mappings file", required=True)
    parser.add_argument(
        "-x", "--text", help="Path to the directory containing the original text", required=True
    )

    parser.add_argument("-v", "--visualization_html_path",
                        help="The Path to find visualization web pages, default path is [%s]" %
                             visualization_path)
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
        "-se", "--source_file_extension",
        help="any extension appended after docid of source files."
             "Default is [%s]" % source_file_ext)

    args = parser.parse_args()

    if args.text is not None:
        text_dir = args.text

    if args.tokenPath is not None:
        if os.path.isdir(args.tokenPath):
            logger.debug("Will search token files in " + args.tokenPath)
            token_dir = args.tokenPath
        else:
            logger.debug("Cannot find given token directory at " +
                         args.tokenPath +
                         ", will try search for current directory")

    if args.visualization_html_path is not None:
        visualization_path = args.visualization_html_path

    if args.offset_field is not None:
        try:
            token_offset_fields = [int(x) for x in args.offset_field.split(",")]
        except ValueError as _:
            logger.error("Should provide two integer with comma in between")

    if args.token_table_extension is not None:
        token_file_ext = args.token_table_extension

    if args.source_file_extension is not None:
        source_file_ext = args.source_file_extension

    validate()
    parse_mapping_file(open(args.comparison_output))

    prepare_diff_setting(doc_ids_to_score, all_possible_mention_types, all_possible_realis_types,
                         os.path.join(visualization_path, visualization_json_data_subpath))
    start_server()


def validate():
    if not os.path.isdir(text_dir):
        logger.error("Cannot find text directory : [%s], cannot do visualization." % text_dir)
    if not os.path.isdir(token_dir):
        logger.error("Cannot find token directory : [%s], cannot do visualization." % text_dir)
    if os.path.isdir(visualization_path):
        json_dir = os.path.join(visualization_path, visualization_json_data_subpath)
        config_dir = os.path.join(json_dir, config_subpath)
        span_dir = os.path.join(json_dir, span_subpath)
        mkdirs(config_dir)
        mkdirs(span_dir)
        logger.info("Generating Brat annotation at " + visualization_path)
    else:
        logger.error("Visualization directory does not exists! Cannot do visualization. You could specify with -v.")
        sys.exit(1)


def mkdirs(p):
    if not os.path.isdir(p):
        os.makedirs(p)


def prepare_diff_setting(all_doc_ids, all_mention_types, all_realis_types, json_path):
    doc_id_list_json_out = open(os.path.join(json_path, config_subpath, "doc_ids.json"), 'w')
    json.dump(all_doc_ids, doc_id_list_json_out)

    annotation_config_json_out = open(os.path.join(json_path, config_subpath, "annotation_config.json"), 'w')
    json.dump(generate_mention_annotation_setting(all_mention_types, all_realis_types),
              annotation_config_json_out, indent=4)

    doc_id_list_json_out.close()
    annotation_config_json_out.close()


def generate_mention_annotation_setting(all_mention_types, all_realis_types):
    config = {}
    event_types = []
    for mention_type in all_mention_types:
        perfect_event_type_setting = {'type': mention_type, 'labels': [mention_type, mention_type],
                                      'bgColor': basic_event_color,
                                      'borderColor': 'darken'}
        partial_match_event_type_setting = {'type': mention_type + partial_matched_suffix,
                                            'labels': [mention_type, mention_type],
                                            'bgColor': partial_matched_event_color,
                                            'borderColor': 'darken'}
        missing_event_type_setting = {'type': mention_type + missing_event_suffix,
                                      'labels': [mention_type, mention_type],
                                      'bgColor': missing_event_color,
                                      'borderColor': 'darken'}
        incorrect_status_event_type_setting = {'type': mention_type + wrong_status_suffix,
                                               'labels': [mention_type, mention_type],
                                               'bgColor': wrong_status_event_color,
                                               'borderColor': 'darken'}

        event_types.extend([perfect_event_type_setting, partial_match_event_type_setting, missing_event_type_setting,
                            incorrect_status_event_type_setting])

    not_annotated_type = {'type': 'NOT_ANNOTATED',
                          'values': {"NOT_ANNOTATED": {"glyph": "N/A"}},
                          "bool": "NOT_ANNOTATED"}
    realis_wrong = {'type': realis_mismatch_attr, 'values': {realis_mismatch_attr: {"glyph": " ★ "}},
                    "bool": realis_mismatch_attr}
    type_wrong = {'type': type_mismatch_attr, 'values': {type_mismatch_attr: {"glyph": " ✘ "}},
                  "bool": type_mismatch_attr}

    event_attribute_types = [not_annotated_type, realis_wrong, type_wrong]

    for realis_type in all_realis_types:
        type_name = realis_type.title()
        realis_setting = {'type': realis_type,
                          'values': {type_name: {"glyph": type_name}},
                          "bool": type_name}
        event_attribute_types.append(realis_setting)

    config["event_types"] = event_types
    config["event_attribute_types"] = event_attribute_types

    return config


def start_server():
    print("Please use the following URL for visualization, interrupt to stop: ")
    print("http://localhost:%s/" % PORT)
    print("Server log stored at : %s" % os.path.join(visualization_path, log_path))
    os.chdir(visualization_path)
    log_file = open(log_path, 'w')
    sys.stderr = log_file
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", PORT), Handler)
    httpd.serve_forever()


def prepare_diff_data(text, gold_annotations, system_annotations, token_map, json_path, doc_id,
                      assigned_gold_2_system_mapping):
    gold_data, system_data = generate_diff_html(text, gold_annotations, system_annotations, token_map,
                                                assigned_gold_2_system_mapping)
    # if "Conflict_Demonstrate" in json.dumps(system_data):
    # print system_data
    gold_json_out = open(os.path.join(json_path, span_subpath, doc_id + "_gold.json"), 'w')
    system_json_out = open(os.path.join(json_path, span_subpath, doc_id + "_sys.json"), 'w')
    json.dump(gold_data, gold_json_out, indent=4)
    json.dump(system_data, system_json_out, indent=4)
    gold_json_out.close()
    system_json_out.close()


def generate_diff_html(text, gold_annotations, system_annotations, token_map, assigned_gold_2_system_mapping):
    gold_mapping_score = [1] * len(gold_annotations)
    system_mapping_score = [0] * len(system_annotations)

    system_realis_match_marker = [0] * len(system_annotations)
    system_type_match_marker = [0] * len(system_annotations)

    gold_realis_match_marker = [0] * len(gold_annotations)
    gold_type_match_marker = [0] * len(gold_annotations)

    for gold_index, mapped_system_indices_and_scores in enumerate(assigned_gold_2_system_mapping):
        if len(mapped_system_indices_and_scores) > 0:
            for system_index, mapping_score in mapped_system_indices_and_scores:
                system_mapping_score[system_index] = mapping_score
                gold_mapping_score[gold_index] = mapping_score

                if system_annotations[system_index][1][1] == gold_annotations[gold_index][1][1]:
                    system_realis_match_marker[system_index] = 1
                    gold_realis_match_marker[gold_index] = 1

                if system_annotations[system_index][1][0] == gold_annotations[gold_index][1][0]:
                    system_type_match_marker[system_index] = 1
                    gold_type_match_marker[gold_index] = 1
        else:
            gold_mapping_score[gold_index] = 0

    gold_data = create_brat_json(text, gold_annotations, token_map, gold_mapping_score, gold_realis_match_marker,
                                 gold_type_match_marker)
    system_data = create_brat_json(text, system_annotations, token_map, system_mapping_score,
                                   system_realis_match_marker, system_type_match_marker)

    return gold_data, system_data


def create_brat_json(text, all_annotations, token_map, span_matching_score, realis_match_marker,
                     type_match_marker):
    data = {'text': text}
    events = []
    mentions = []
    attributes = []
    text_bound_id_record = [{}, 1]
    attribute_id_record = [{}, 1]
    # event_id_record = [{}, 1]

    for index, (token_based_annotations, (mention_type, realis), event_id) in enumerate(all_annotations):
        text_bound_id, annotation = parse_token_annotation(token_based_annotations, token_map, text_bound_id_record)
        span_status = span_matching_score[index]

        perfect_span = False

        if span_status == 0:
            mention = [text_bound_id, mention_type + missing_event_suffix, annotation]
        elif span_status < 1.0:
            mention = [text_bound_id, mention_type + partial_matched_suffix, annotation]
        else:
            perfect_span = True

        # event_id = auto_find_id(event_id_record, text_bound_id, "E")

        realis_attribute_id = auto_find_id(attribute_id_record, (realis, text_bound_id, event_id), "A")
        event_realis = [realis_attribute_id, realis, event_id]
        event = [event_id, text_bound_id, []]

        realis_status = 1 if realis_match_marker is None else realis_match_marker[index]
        if realis_status == 0:
            realis_mismatch_id = auto_find_id(attribute_id_record, (realis_mismatch_attr, realis_attribute_id), "A")
            realis_mismatch = [realis_mismatch_id, realis_mismatch_attr, event_id]
            attributes.append(realis_mismatch)

        type_status = 1 if type_match_marker is None else type_match_marker[index]
        if type_status == 0:
            type_mismatch_id = auto_find_id(attribute_id_record, (type_mismatch_attr, event_id), "A")
            type_mismatch = [type_mismatch_id, type_mismatch_attr, event_id]
            attributes.append(type_mismatch)

        if perfect_span:
            if type_status == 0 or realis_status == 0:
                mention = [text_bound_id, mention_type + wrong_status_suffix, annotation]
            else:
                mention = [text_bound_id, mention_type, annotation]

        events.append(event)
        mentions.append(mention)
        attributes.append(event_realis)

    data['triggers'] = mentions
    data['attributes'] = attributes
    data['events'] = events
    return data


def parse_token_annotation(token_based_annotations, token_map, text_span_id):
    """
    Create JSON based annotation to be embedded using Brat
    :param token_based_annotations: The annotations, in terms of token ids
    :param token_map: The token id to character span mapping
    :param mention_type: The mention_type of the annotation
    :param text_span_id: Map from text span to id
    :return: JSON data representing the annotation
    """
    return assign_text_bound_id(token_annotation_2_character_annotation(token_based_annotations, token_map),
                                text_span_id)


def token_annotation_2_character_annotation(token_based_annotations, token_map):
    """
    Convert a token based annotation into character based. Discontinuous annotations are handled

    :param token_based_annotations: Annotations in terms of tokens
    :param token_map: Token id to character span mapping
    :return: The result character based annotation
    """
    spans = []
    last_id = -1

    for sorted_token in sorted(token_based_annotations, key=natural_key):
        print sorted_token
        sys.stdin.readline()
        this_id = ''.join(str(x) for x in natural_key(sorted_token))
        if last_id == -1 or this_id != last_id + 1:
            spans.append([])
            # if last_id != -1:
            #     print "Adding %s to %s" % (this_id, last_id)
            #     sys.stdin.readline()
            # else:
            #     print "Adding %s" % this_id
        spans[-1].append(sorted_token)
    return [[token_map[s[0]][0], token_map[s[-1]][1] - 1] for s in spans]


def natural_key(string_):
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]


def token_2_string_id(int_id):
    # return "t%d" % int_id
    # Assuming token id in 't1, t2' format.
    return "%d" % int_id


def token_2_int_id(token_id):
    # Assuming token id in 't1, t2' format.
    # return int(token_id[1:])
    return int(token_id)


def auto_find_id(id_record, key, prefix):
    if key in id_record[0]:
        return id_record[0][key]
    else:
        id = prefix + str(id_record[1])
        id_record[1] += 1
        id_record[0][0] = id
        return id


def assign_text_bound_id(character_based_annotations, text_bound_id_record):
    """
    Create JSON based annotation to be embedded using Brat
    :param character_based_annotations: The annotations, in terms of character offset
    :param text_bound_id_record: Map from text span to id
    :return: JSON data representing the annotation
    """
    key = repr(character_based_annotations)
    tid = auto_find_id(text_bound_id_record, key, "T")

    return tid, character_based_annotations


def parse_mapping_line(l):
    main_parts = l.split("\t|\t")
    gold_parts = main_parts[0].split("\t")
    sys_parts = main_parts[1].split("\t")
    sys_id = gold_parts[0]
    gold_fields = gold_parts[1:]
    score = sys_parts[-1]
    sys_fields = sys_parts[:-1]
    return sys_id, gold_fields, sys_fields, score


def read_token_ids(g_file_name):
    id2token_map = {}
    token_file_path = os.path.join(token_dir, g_file_name + token_file_ext)
    logger.debug("Reading token for " + g_file_name)

    try:
        token_file = open(token_file_path)
        # discard the header
        header = token_file.readline()

        for tline in token_file:
            fields = tline.rstrip().split("\t")
            if len(fields) < 4:
                logger.debug("Weird token line " + tline)
                continue

            token_id = fields[0]

            try:
                token_span = (int(fields[token_offset_fields[0]]), int(fields[token_offset_fields[1]]) + 1)
                id2token_map[token_id] = token_span
            except ValueError as e:
                logger.error("Token file is wrong at for file " + g_file_name)
    except IOError:
        logger.debug(
            "Cannot find token file for doc [%s] at [%s]" % (g_file_name, token_file_path))
        pass
    return id2token_map


def read_original_text(doc_id):
    text_path = os.path.join(text_dir, doc_id + source_file_ext)
    if os.path.exists(text_path):
        f = open(os.path.join(text_dir, doc_id + source_file_ext))
        return f.read()
    else:
        logger.error("Cannot locate original text, please check parameters")
        sys.exit(1)


def parse_mapping(doc_id, doc_lines):
    gold_annotations = []
    system_annotations = []
    token_map = read_token_ids(doc_id)

    num_gold_mentions = 0
    for l in doc_lines:
        sys_id, gold_fields, sys_fields, score = parse_mapping_line(l)
        if gold_fields[0] != "-":
            num_gold_mentions += 1

    assigned_gold_2_system_mapping = [[] for _ in xrange(num_gold_mentions)]

    gold_index = 0
    sys_index = 0
    for l in doc_lines:
        sys_id, gold_fields, sys_fields, score = parse_mapping_line(l)
        # print l
        # print gold_fields, sys_fields, score
        # sys.stdin.readline()
        if score != "-":
            assigned_gold_2_system_mapping[gold_index].append((sys_index, float(score)))
        if gold_fields[0] != "-":
            gold_annotations.append((gold_fields[1].split(token_joiner), gold_fields[2:], gold_fields[0]))
            all_possible_mention_types.add(gold_fields[2])
            all_possible_realis_types.add(gold_fields[3])
            gold_index += 1
        if sys_fields[0] != "-":
            system_annotations.append((sys_fields[1].split(token_joiner), sys_fields[2:], gold_fields[0]))
            all_possible_mention_types.add(sys_fields[2])
            all_possible_realis_types.add(sys_fields[3])
            sys_index += 1

    text = read_original_text(doc_id)

    prepare_diff_data(text, gold_annotations, system_annotations, token_map,
                      os.path.join(visualization_path, visualization_json_data_subpath), doc_id,
                      assigned_gold_2_system_mapping)

    doc_ids_to_score.append(doc_id)


def parse_mapping_file(f):
    doc_lines = []
    doc_id = ""

    for l in f.readlines():
        l = l.strip()
        if l.startswith(comment_marker):
            if l.startswith(bod_marker):
                doc_id = l[len(bod_marker):].strip()
            elif l.startswith(eod_marker):
                parse_mapping(doc_id, doc_lines)
                doc_lines = []
        elif l == "":
            pass
        else:
            doc_lines.append(l)


if __name__ == "__main__":
    main()

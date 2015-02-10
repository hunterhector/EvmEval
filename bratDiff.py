#!/usr/bin/python

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

PORT = 8000

log_path = "server_log"
basic_event_color = "lightgreen"
missing_event_color = "#ffccaa"
partial_matched_event_color = "#aea0d6"
missing_event_suffix = "_miss"
partial_matched_suffix = "_part"
realis_mismatch_attr = "realis_wrong"
type_mismatch_attr = "type_wrong"


def prepare_diff_setting(all_doc_ids, all_mention_types, json_path):
    doc_id_list_json_out = open(os.path.join(json_path, "doc_ids.json"), 'w')
    doc_id_list_json_out.write(json.dumps(all_doc_ids))

    annotation_config_json_out = open(os.path.join(json_path, "annotation_config.json"), 'w')
    annotation_config_json_out.write(generate_mention_annotation_setting(all_mention_types))


def generate_mention_annotation_setting(all_mention_types):
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
        event_types.extend([perfect_event_type_setting, partial_match_event_type_setting, missing_event_type_setting])

    generic_type = {'type': 'Generic', 'values': {"Generic": {"glyph": "generic"}}, "bool": "Generic"}
    other_type = {'type': 'Other', 'values': {"Other": {"glyph": "other"}}, "bool": "Other"}
    actual_type = {'type': 'Actual', 'values': {"Generic": {"glyph": "actual"}}, "bool": "Actual"}
    not_annotated_type = {'type': 'NOT_ANNOTATED', 'values': {"NOT_ANNOTATED": {"glyph": "N/A"}},
                          "bool": "NOT_ANNOTATED"}

    realis_wrong = {'type': realis_mismatch_attr, 'values': {realis_mismatch_attr: {"glyph": "*"}},
                    "bool": realis_mismatch_attr}

    type_wrong = {'type': type_mismatch_attr, 'values': {type_mismatch_attr: {"glyph": "#"}},
                  "bool": type_mismatch_attr}

    event_attribute_types = [generic_type, other_type, actual_type, not_annotated_type, realis_wrong, type_wrong]

    config["event_types"] = event_types
    config["event_attribute_types"] = event_attribute_types

    return json.dumps(config, indent=4)


def start_server(visualization_path, logger):
    logger.info("Please use the following URL for visualization, interrupt to stop: ")
    logger.info("http://localhost:%s/" % PORT)
    logger.info("Server log stored at : %s" % os.path.join(visualization_path, log_path))
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
    gold_json_out = open(os.path.join(json_path, doc_id + "_gold.json"),
                         'w')
    system_json_out = open(os.path.join(json_path, doc_id + "_sys.json"),
                           'w')
    gold_json_out.write(gold_data)
    system_json_out.write(system_data)


def generate_diff_html(text, gold_annotations, system_annotations, token_map, assigned_gold_2_system_mapping):
    gold_missing_marker = [1] * len(gold_annotations)
    system_missing_marker = [0] * len(system_annotations)

    system_realis_match_marker = [0] * len(system_annotations)
    system_type_match_marker = [0] * len(system_annotations)

    gold_realis_match_marker = [0] * len(gold_annotations)
    gold_type_match_marker = [0] * len(gold_annotations)

    for gold_index, (system_indices, score) in enumerate(
            assigned_gold_2_system_mapping):
        if score > 0:  # -1 indicates no mapping

            for system_index in system_indices:
                system_missing_marker[system_index] = score
                gold_missing_marker[gold_index] = score

                if (system_annotations[system_index][2] ==
                        gold_annotations[gold_index][2]):
                    system_realis_match_marker[system_index] = 1
                    gold_realis_match_marker[gold_index] = 1

                if (system_annotations[system_index][1] ==
                        gold_annotations[gold_index][1]):
                    system_type_match_marker[system_index] = 1
                    gold_type_match_marker[gold_index] = 1
        else:
            gold_missing_marker[gold_index] = 0

    gold_data = create_brat_json(text, gold_annotations, token_map, gold_missing_marker, gold_realis_match_marker,
                                 gold_type_match_marker)
    system_data = create_brat_json(text, system_annotations, token_map, system_missing_marker,
                                   system_realis_match_marker, system_type_match_marker)
    return gold_data, system_data


def create_brat_json(text, all_annotations, token_map, span_missing_marker, realis_match_marker,
                     type_match_marker):
    data = {'text': text}
    events = []
    mentions = []
    attributes = []
    text_bound_id_record = [{}, 1]
    attribute_id_record = [{}, 1]
    event_id_record = [{}, 1]

    for index, (token_based_annotations, mention_type, realis) in enumerate(all_annotations):
        text_bound_id, annotation = parse_token_annotation(token_based_annotations, token_map, text_bound_id_record)
        span_status = span_missing_marker[index]
        if span_status == 0:
            mention = [text_bound_id, mention_type + missing_event_suffix, annotation]
        elif span_status < 1:
            mention = [text_bound_id, mention_type + partial_matched_suffix, annotation]
        else:
            mention = [text_bound_id, mention_type, annotation]
        event_id = auto_find_id(event_id_record, text_bound_id, "E")

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

        events.append(event)
        mentions.append(mention)
        attributes.append(event_realis)
    data['triggers'] = mentions
    data['attributes'] = attributes
    data['events'] = events
    return json.dumps(data, indent=4)


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
    Convert a token based annotation into character based. Assuming token id in
    't1, t2' format. Discontinuous annotations are handled

    :param token_based_annotations: Annotations in terms of tokens
    :param token_map: Token id to character span mapping
    :return: The result character based annotation
    """
    spans = []
    last_id = -1

    for sorted_token in sorted(token_based_annotations, key=lambda x: token_2_int_id(x)):
        this_id = token_2_int_id(sorted_token)
        if last_id == -1 or this_id != last_id + 1:
            spans.append([])
        spans[-1].append(token_2_string_id(this_id))

    return [[token_map[s[0]][0], token_map[s[-1]][1] + 1] for s in spans]


def token_2_string_id(int_id):
    return "t%d" % int_id


def token_2_int_id(token_id):
    return int(token_id[1:])


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
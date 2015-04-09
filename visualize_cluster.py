#!/usr/bin/python
# coding=utf-8

"""
    Used together with the visualizer, provide data for coreference

    Visualization is done via embedded Brat tool

    Author: Zhengzhong Liu ( liu@cs.cmu.edu )
"""

__author__ = 'zhengzhongliu'

import argparse
import logging
import sys
import os
import json

brat_annotation_ext = ".tkn.ann"
visualization_path = "visualization"
visualization_json_data_subpath = "json"
coref_subpath = "coref"
surface_subpath = "surface"

relation_marker = "R"
span_marker = "T"
event_marker = "E"
coreference_relation_name = "Coreference"

logger = logging.getLogger()
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s : %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)


def main():
    global visualization_path
    global brat_annotation_ext

    parser = argparse.ArgumentParser(
        description="Cluster visualizer, will add more data to help create"
                    " a side-by-side embedded visualization for coreference "
    )

    parser.add_argument("-g", "--gold_dir", help="directory of the gold annotation files", required=True)
    parser.add_argument("-s", "--sys_dir", help="directory of the system annotation files", required=True)

    parser.add_argument("-ae", "--annotation_extension",
                        help="any extension appended after docid of annotation files. "
                             "Default is " + brat_annotation_ext)

    parser.add_argument("-v", "--visualization_html_path",
                        help="The Path to find visualization web pages, default path is [%s]" %
                             visualization_path)

    args = parser.parse_args()

    if args.gold_dir is not None and args.sys_dir is not None:
        # parse directory
        for f in os.listdir(args.gold_dir):
            if f.endswith(brat_annotation_ext):
                write_coreference_json(os.path.join(args.gold_dir, f), os.path.join(args.sys_dir, f),
                                       os.path.join(visualization_path, visualization_json_data_subpath))


def write_coreference_json(gold_path, sys_path, parent_path):
    basename = os.path.basename(gold_path)
    logger.debug("Processing " + basename)

    coref_dir = os.path.join(parent_path, coref_subpath)
    surface_dir = os.path.join(parent_path, surface_subpath)

    if os.path.isfile(gold_path) and os.path.isfile(sys_path):
        g = open(gold_path)
        s = open(sys_path)
        text_id = rchop(basename, brat_annotation_ext)
        logger.debug("Document id is " + text_id)

        g_coref, g_text = read_coreference(g)
        s_coref, s_text = read_coreference(s)

        dump_json(g_coref, coref_dir, text_id, "_coref_gold.json")
        dump_json(s_coref, coref_dir, text_id, "_coref_sys.json")
        dump_json(g_text, surface_dir, text_id, "_surface_gold.json")
        dump_json(s_text, surface_dir, text_id, "_surface_sys.json")
    else:
        logger.info("System do not contains : " + basename)


def dump_json(data, json_path, text_id, suffix):
    if not os.path.isdir(json_path):
        os.makedirs(json_path)
    o = open(os.path.join(json_path, text_id + suffix), 'w')
    json.dump(data, o, indent=4)
    o.close()


def read_coreference(f):
    clusters = []
    textspan = {}
    event_2_text_span_id = {}

    for l in f:
        parts = l.strip().split("\t")
        if l.startswith(relation_marker):
            relation = parts[1]
            link = read_coref_link(relation)

            if link:
                e1, e2 = link
                for cluster in clusters:
                    if e1 in cluster or e2 in cluster:
                        cluster.add(e1)
                        cluster.add(e2)
                else:
                    clusters.append({e1, e2})
        elif l.startswith(event_marker):
            eid = parts[0]
            span_id = parts[1].split(":")[1]
            event_2_text_span_id[eid] = span_id
        elif l.startswith(span_marker):
            textspan[parts[0]] = parts[2]

    cluster_json = []
    for cluster in clusters:
        cluster_json.append(list(cluster))

    event_text_json = {}
    for eid, tid in event_2_text_span_id.iteritems():
        if tid in textspan:
            text = textspan[tid]
            event_text_json[eid] = text

    return cluster_json, event_text_json


def read_coref_link(r):
    t, a1, a2 = r.split(" ")
    if t == coreference_relation_name:
        return chop(a1, "Arg1:"), chop(a2, "Arg2:")


def chop(s, begin):
    if s.startswith(begin):
        return s[len(begin):]
    return s


def rchop(s, ending):
    if s.endswith(ending):
        return s[:-len(ending)]
    return s


if __name__ == "__main__":
    main()
#!/usr/bin/python

"""
Utilities to convert AFTER relations into TimeML format and compute the scoring using TimeML tools.
"""

import logging
import os
import subprocess
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from config import Config

logger = logging.getLogger(__name__)


def validate(events, edges):
    """
    Validate whether the edges are valid. Currently, the validation only check whether the reverse is also included,
    which is not possible for after links.
    :param edges:
    :return:
    """
    reverse_edges = set()

    for edge in edges:
        left = edge[0]
        right = edge[1]
        t = edges[2]

        if left not in events:
            logger.error("Relation contains unknown event %s." % left)
        if right not in events:
            logger.error("Relation contains unknown event %s." % right)

        if edge in reverse_edges:
            logger.error("There is a link from %s to %s and %s to %s, this is not allowed."
                         % (left, right, right, left))
            return False

        reverse_edges.add((right, left, t))
    return True


def make_event(parent, eid):
    event = SubElement(parent, "EVENT")
    event.set("eid", eid)


def create_root():
    timeml = Element('TimML')
    timeml.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    timeml.set("xsi:noNamespaceSchemaLocation", "http://timeml.org/timeMLdocs/TimeML_1.2.1.xsd")

    # Add a dummy DCT (document creation time).
    dct = SubElement(timeml, "DCT")
    timex3 = SubElement(dct, "TIMEX3")
    timex3.set("tid", "t0")
    timex3.set("type", "TIME")
    timex3.set("value", "")
    timex3.set("temporalFunction", "false")
    timex3.set("functionInDocument", "CREATION_TIME")

    return timeml


def convert_links(links):
    converted = []
    for l in links:
        relation_name = convert_name(l[0])
        args = l[2]
        converted.append((args[0], args[1], relation_name))
    return converted


def convert_name(name):
    if name == "After":
        return "AFTER"


def pretty_print(element):
    """
    Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


class TemporalEval:
    """
    This class help us converting the input into TLINK format and evaluate them using the temporal evaluation tools
    developed by UzZaman. We use the variation of their method that use both the reduced graph and rewarding
    un-inferable implicit relations.

    Reference:
    Interpreting the Temporal Aspects of Language, Naushad UzZaman, 2012
    """

    def __init__(self, doc_id, g2s_mapping, gold_nuggets, gold_links, sys_nuggets, sys_links):
        # if not validate(events, edges):
        #     raise RuntimeError("The edges cannot form a valid temporal graph.")

        self.gold_nodes = []
        self.sys_nodes = []

        self.normalized_system_nodes = {}
        self.normalized_gold_nodes = {}
        self.convert_to_t_mapping(g2s_mapping, gold_nuggets, sys_nuggets)

        self.gold_nuggets = gold_nuggets
        self.sys_nuggets = sys_nuggets

        self.gold_time_ml = self.make_time_ml(convert_links(gold_links), self.normalized_gold_nodes, self.gold_nodes)
        self.sys_time_ml = self.make_time_ml(convert_links(sys_links), self.normalized_system_nodes, self.sys_nodes)

        self.doc_id = doc_id

    def write_time_ml(self):
        # Write out the temporal files to disk.
        gold_temp_file = open(
            os.path.join(Config.temporal_result_dir, Config.temporal_gold_dir, "%s.tml" % self.doc_id), 'w')
        sys_temp_file = open(os.path.join(Config.temporal_result_dir, Config.temporal_sys_dir,
                                          "%s.tml" % self.doc_id), 'w')

        gold_temp_file.write(pretty_print(self.gold_time_ml))
        sys_temp_file.write(pretty_print(self.sys_time_ml))

        gold_temp_file.close()
        sys_temp_file.close()

    @staticmethod
    def eval_time_ml():
        logger.info("Running TimeML scorer.")

        temporal_output = os.path.join(Config.temporal_result_dir, Config.temporal_out)

        gold_dir = os.path.join(Config.temporal_result_dir, Config.temporal_gold_dir)
        sys_dir = os.path.join(Config.temporal_result_dir, Config.temporal_sys_dir)

        with open(temporal_output, 'wb', 0) as out_file:
            subprocess.call(["python", Config.temp_eval_executable, gold_dir, sys_dir, '0', "implicit_in_recall"],
                            stdout=out_file)

    @staticmethod
    def get_eval_output():
        temporal_output = os.path.join(Config.temporal_result_dir, Config.temporal_out)
        with open(temporal_output, 'r') as f:
            score_line = False
            for l in f:
                if score_line:
                    prec, recall, f1 = [float(x) for x in l.strip().split("\t")]
                    return prec, recall, f1

                if l.startswith("Temporal Score"):
                    score_line = True


    def convert_to_t_mapping(self, e_mapping, gold_nuggets, system_nuggets):
        mapped_system_mentions = set()

        tid = 0
        for gold_index, (system_index, _) in enumerate(e_mapping):
            node_id = "te%d" % tid
            tid += 1

            print "Gold %d is mapped to system %d, node id %s" % (gold_index, system_index, node_id)

            gold_temporal_instance_id = gold_nuggets[gold_index][5]
            self.normalized_gold_nodes[gold_temporal_instance_id] = node_id
            self.gold_nodes.append(node_id)

            if system_index != -1:
                system_temporal_instance_id = system_nuggets[system_index][5]
                self.normalized_system_nodes[system_temporal_instance_id] = node_id
                self.sys_nodes.append(node_id)
                mapped_system_mentions.add(system_index)

        for system_index, system_nugget in enumerate(system_nuggets):
            if system_index not in mapped_system_mentions:
                node_id = "te%d" % tid
                tid += 1

                system_temporal_instance_id = system_nugget[5]
                self.normalized_system_nodes[system_temporal_instance_id] = node_id
                self.sys_nodes.append(node_id)

    def make_time_ml(self, links, normalized_nodes, nodes):
        # Create the root.
        time_ml = create_root()

        # Add the text node.
        text = SubElement(time_ml, "TEXT")
        self.annotate_timeml_events(text, nodes)

        # Add instances.
        self.create_instance(time_ml, nodes)

        # Add TLINKs.
        self.create_tlinks(time_ml, links, normalized_nodes)

        return time_ml

    def create_instance(self, parent, nodes):
        for node in nodes:
            instance = SubElement(parent, "MAKEINSTANCE")
            instance.set("eiid", "instance_" + node)
            instance.set("eid", node)

    def annotate_timeml_events(self, text_node, nodes):
        for tid in nodes:
            make_event(text_node, tid)

    def create_tlinks(self, time_ml, links, normalized_nodes):
        lid = 0

        for left, right, rType in links:
            normalized_left = normalized_nodes[left]
            normalized_right = normalized_nodes[right]

            link = SubElement(time_ml, "TLINK")
            link.set("lid", "l%d" % lid)
            link.set("relType", rType)
            link.set("eventInstanceID", normalized_left)
            link.set("relatedToEventInstance", normalized_right)

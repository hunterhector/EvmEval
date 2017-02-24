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
from utils import TransitiveGraph
import utils

logger = logging.getLogger(__name__)


def validate(nuggets, edges_by_type):
    """
    Validate whether the edges are valid. Currently, the validation only check whether the reverse is also included,
    which is not possible for after links.
    :param nuggets: The set of possible nuggets.
    :param edges: Edges in the system.
    :return:
    """
    for name, edges in edges_by_type.iteritems():
        reverse_edges = set()

        for edge in edges:
            left, right, t = edge

            if left not in nuggets:
                logger.error("Relation contains unknown event %s." % left)
            if right not in nuggets:
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


def convert_links(links_by_name):
    all_converted = {}
    for name, links in links_by_name.iteritems():
        converted = []
        for l in links:
            relation_name = convert_name(l[2])
            converted.append((l[0], l[1], relation_name))
        all_converted[name] = converted

    return all_converted


def convert_name(name):
    '''
    Convert the Event Sequencing names to an corresponding TimeML name for evaluation.
    Note that, the meaning of After in event sequencing is different from TimeML specification.

    In Event Sequencing task, E1 --after--> E2 represent a directed link, where the latter one happens later. In TIMEML,
    E1 --after--> E2 actually says E1 is after E2. So we use the BEFORE tag instead.

    This conversion is just for the sake of logically corresponding, in fact, converting to "BEFORE" and "AFTER" will
    produce the same scores.

    In addiction, in TIMEML, there is no definition for Subevent, but "INCLUDES" have a similar semantic with that.

    :param name:
    :return:
    '''
    if name == "After":
        return "BEFORE"
    elif name == "Subevent":
        return "INCLUDES"
    else:
        logger.warn("Unsupported relations name %s found." % name)


def pretty_xml(element):
    """
    Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def find_equivalent_sets(clusters, nuggets):
    nodes = [nugget[2] for nugget in nuggets]

    node_2_set = {}
    set_2_nodes = {}
    non_singletons = set()

    set_id = 0

    for cluster in clusters:
        for element in cluster[2]:
            node_2_set[element] = set_id
            non_singletons.add(element)

            try:
                set_2_nodes[set_id].append(element)
            except KeyError:
                set_2_nodes[set_id] = [element]

        set_id += 1

    for node in nodes:
        if node not in non_singletons:
            node_2_set[node] = set_id
            try:
                set_2_nodes[set_id].append(node)
            except KeyError:
                set_2_nodes[set_id] = [node]

            set_id += 1

    return set_2_nodes, node_2_set


def propagate_through_equivalence(links_by_name, equivalent_links, nuggets):
    set_2_nodes, node_2_set = find_equivalent_sets(equivalent_links, nuggets)

    all_expanded_links = {}

    for name, links in links_by_name.iteritems():
        set_links = []

        for link in links:
            relation = link[0]
            arg1, arg2 = link[2]
            set_links.append((node_2_set[arg1], node_2_set[arg2], relation))

        reduced_set_links = compute_reduced_graph(set_links)

        expanded_links = set()

        for link in reduced_set_links:
            arg1, arg2, relation = link

            for node1 in set_2_nodes[arg1]:
                for node2 in set_2_nodes[arg2]:
                    expanded_links.add((node1, node2, relation))

        all_expanded_links[name] = list(expanded_links)

    return all_expanded_links


def compute_reduced_graph(set_links):
    node_indices = utils.get_nodes(set_links)

    graph = TransitiveGraph(len(node_indices))

    for arg1, arg2, relation in set_links:
        node_index1 = node_indices[arg1]
        node_index2 = node_indices[arg2]
        graph.add_edge(node_index1, node_index2)

    closure_matrix = graph.transitive_closure()

    indirect_links = set()

    for from_node, to_nodes in enumerate(closure_matrix):
        for to_node, reachable in enumerate(to_nodes):
            if from_node != to_node and reachable == 1:
                for indirect_node, indirect_reachable in enumerate(closure_matrix[to_node]):
                    if indirect_node != to_node:
                        if indirect_reachable == 1:
                            indirect_links.add((from_node, indirect_node))

    reduced_links = []

    for arg1, arg2, relation in set_links:
        node_index1 = node_indices[arg1]
        node_index2 = node_indices[arg2]

        if (node_index1, node_index2) not in indirect_links:
            reduced_links.append((arg1, arg2, relation))

    return reduced_links


class TemporalEval:
    """
    This class help us converting the input into TLINK format and evaluate them using the temporal evaluation tools
    developed by UzZaman. We use the variation of their method that use both the reduced graph and rewarding
    un-inferable implicit relations.

    Reference:
    Interpreting the Temporal Aspects of Language, Naushad UzZaman, 2012
    """

    def __init__(self, doc_id, g2s_mapping, gold_nuggets, gold_links, sys_nuggets, sys_links, gold_corefs, sys_corefs):
        gold_links_by_type = propagate_through_equivalence(gold_links, gold_corefs, gold_nuggets)
        sys_links_by_type = propagate_through_equivalence(sys_links, sys_corefs, gold_nuggets)

        self.normalized_system_nodes = {}
        self.normalized_gold_nodes = {}

        self.gold_nuggets = gold_nuggets
        self.sys_nuggets = sys_nuggets

        self.gold_nodes = []
        self.sys_nodes = []

        self.store_nodes(g2s_mapping)

        if not Config.no_temporal_validation:
            if not validate(set([nugget[2] for nugget in gold_nuggets]), gold_links_by_type):
                raise RuntimeError("The gold standard edges cannot form a valid temporal graph.")

            if not validate(set([nugget[2] for nugget in sys_nuggets]), sys_links_by_type):
                raise RuntimeError("The system edges cannot form a valid temporal graph.")

        self.gold_time_ml = self.make_all_time_ml(convert_links(gold_links_by_type), self.normalized_gold_nodes,
                                                  self.gold_nodes)
        self.sys_time_ml = self.make_all_time_ml(convert_links(sys_links_by_type), self.normalized_system_nodes,
                                                 self.sys_nodes)

        self.doc_id = doc_id

    def write_time_ml(self):
        """
        Write the TimeML file to disk.
        :return:
        """
        self.write(self.gold_time_ml, Config.temporal_gold_dir)
        self.write(self.sys_time_ml, Config.temporal_sys_dir)

    def write(self, time_ml_data, subdir):
        """
        Write out time ml files into sub directories.
        :param time_ml_data:
        :param time_ml_dir:
        :param subdir:
        :return:
        """
        for name, time_ml in time_ml_data.iteritems():
            output_dir = os.path.join(Config.temporal_result_dir, name, subdir)

            if not os.path.isdir(output_dir):
                utils.supermakedirs(output_dir)

            temp_file = open(os.path.join(output_dir, "%s.tml" % self.doc_id), 'w')
            temp_file.write(pretty_xml(time_ml))
            temp_file.close()

            logger.info("Write out tml into " + output_dir+  "/" + self.doc_id)

    @staticmethod
    def eval_time_ml():
        logger.info("Running TimeML scorer.")

        for link_type in os.listdir(Config.temporal_result_dir):
            print link_type
            temporal_output = os.path.join(Config.temporal_result_dir, link_type, Config.temporal_out)

            gold_sub_dir = os.path.join(Config.temporal_result_dir, link_type, Config.temporal_gold_dir)
            sys_sub_dir = os.path.join(Config.temporal_result_dir, link_type, Config.temporal_sys_dir)

            with open(temporal_output, 'wb', 0) as out_file:
                subprocess.call(["python", Config.temp_eval_executable, gold_sub_dir, sys_sub_dir,
                                 '0', "implicit_in_recall"], stdout=out_file)

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

    def store_nodes(self, e_mapping):
        mapped_system_mentions = set()

        tid = 0
        for gold_index, (system_index, _) in enumerate(e_mapping):
            node_id = "te%d" % tid
            tid += 1

            gold_temporal_instance_id = self.gold_nuggets[gold_index][2]
            self.normalized_gold_nodes[gold_temporal_instance_id] = node_id
            self.gold_nodes.append(node_id)

            if system_index != -1:
                system_temporal_instance_id = self.sys_nuggets[system_index][2]
                self.normalized_system_nodes[system_temporal_instance_id] = node_id
                self.sys_nodes.append(node_id)
                mapped_system_mentions.add(system_index)

        for system_index, system_nugget in enumerate(self.sys_nuggets):
            if system_index not in mapped_system_mentions:
                node_id = "te%d" % tid
                tid += 1

                system_temporal_instance_id = system_nugget[2]
                self.normalized_system_nodes[system_temporal_instance_id] = node_id
                self.sys_nodes.append(node_id)

    def make_all_time_ml(self, links_by_name, normalized_nodes, nodes):
        all_time_ml = {}

        all_links = []

        for name, links in links_by_name.iteritems():
            all_time_ml[name] = self.make_time_ml(links, normalized_nodes, nodes)
            all_links.extend(links)

        all_time_ml["All"] = self.make_time_ml(all_links, normalized_nodes, nodes)

        return all_time_ml

    def make_time_ml(self, links, normalized_nodes, nodes):
        # Create the root.
        time_ml = create_root()
        # Add TEXT.
        self.annotate_timeml_events(time_ml, nodes)

        # Add instances.
        self.create_instance(time_ml, nodes)
        self.create_tlinks(time_ml, links, normalized_nodes)

        return time_ml

    def create_instance(self, parent, nodes):
        for node in nodes:
            instance = SubElement(parent, "MAKEINSTANCE")
            instance.set("eiid", "instance_" + node)
            instance.set("eid", node)

    def annotate_timeml_events(self, parent, nodes):
        text = SubElement(parent, "TEXT")
        for tid in nodes:
            make_event(text, tid)

    def create_tlinks(self, time_ml, links, normalized_nodes):
        lid = 0

        for left, right, relation_type in links:
            if left not in normalized_nodes:
                logger.error("Node %s is not a event mention." % left)
                continue

            if right not in normalized_nodes:
                logger.error("Node %s is not a event mention." % right)
                continue

            normalized_left = normalized_nodes[left]
            normalized_right = normalized_nodes[right]

            link = SubElement(time_ml, "TLINK")
            link.set("lid", "l%d" % lid)
            link.set("relType", relation_type)
            link.set("eventInstanceID", normalized_left)
            link.set("relatedToEventInstance", normalized_right)

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
    """
    Convert the Event Sequencing names to an corresponding TimeML name for evaluation.
    Note that, the meaning of After in event sequencing is different from TimeML specification.

    In Event Sequencing task, E1 --after--> E2 represent a directed link, where the latter one happens later. In TIMEML,
    E1 --after--> E2 actually says E1 is after E2. So we use the BEFORE tag instead.

    This conversion is just for the sake of logically corresponding, in fact, converting to "BEFORE" and "AFTER" will
    produce the same scores.

    In addiction, in TIMEML, there is no definition for Subevent, but "INCLUDES" have a similar semantic with that.

    :param name:
    :return:
    """
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


def find_equivalent_sets(clusters, nodes):
    node_2_set = {}
    set_2_nodes = {}
    non_singletons = set()

    set_index = 0

    for cluster in clusters:
        for element in cluster[2]:
            node_2_set[element] = "c%d" % set_index
            non_singletons.add(element)

            try:
                set_2_nodes["c%d" % set_index].append(element)
            except KeyError:
                set_2_nodes["c%d" % set_index] = [element]

        set_index += 1

    for node in nodes:
        if node not in non_singletons:
            node_2_set[node] = "c%d" % set_index
            try:
                set_2_nodes["c%d" % set_index].append(node)
            except KeyError:
                set_2_nodes["c%d" % set_index] = [node]

            set_index += 1

    return set_2_nodes, node_2_set


def convert_to_cluster_links(node_links_by_name, cluster_lookup):
    cluster_links_by_name = {}

    for name, node_links in node_links_by_name.iteritems():
        cluster_links = set()

        for node1, node2, link_type in node_links:
            cluster1 = cluster_lookup[node1]
            cluster2 = cluster_lookup[node2]
            cluster_links.add((cluster1, cluster2, link_type))

        cluster_links_by_name[name] = cluster_links

    return cluster_links_by_name


def propagate_through_equivalence(links_by_name, set_2_nodes, node_2_set):
    # set_2_nodes, node_2_set = find_equivalent_sets(equivalent_links, nuggets)

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


def run_eval(link_type, temporal_output, gold_dir, sys_dir):
    gold_sub_dir = os.path.join(Config.temporal_result_dir, link_type, gold_dir)
    sys_sub_dir = os.path.join(Config.temporal_result_dir, link_type, sys_dir)

    with open(temporal_output, 'wb', 0) as out_file:
        subprocess.call(["python", Config.temp_eval_executable, gold_sub_dir, sys_sub_dir,
                         '0', "implicit_in_recall"], stdout=out_file)


def rewrite_lookup(gold_cluster_lookup, g2s_mapping, gold_nugget_table, sys_nugget_table):
    """
    Rewrite the gold nugget id to cluster id lookup, as system nugget id to cluster id lookup.
    :param gold_cluster_lookup: The gold cluster id lookup table.
    :param g2s_mapping: Mapping from gold to system.
    :param gold_nugget_table: Stores the gold nugget id.
    :param sys_nugget_table: Stores the system nugget id.
    :return:
    """
    rewritten_lookup = {}

    gold_id_2_system_id = {}
    for gold_index, (sys_index, _) in enumerate(g2s_mapping):
        gold_nugget_id = gold_nugget_table[gold_index][2]
        sys_nugget_id = sys_nugget_table[sys_index][2]

        gold_id_2_system_id[gold_nugget_id] = sys_nugget_id

    for gold_nugget_id, cluster_id in gold_cluster_lookup.iteritems():
        sys_nugget_id = gold_id_2_system_id[gold_nugget_id]
        rewritten_lookup[sys_nugget_id] = cluster_id

    return rewritten_lookup


class TemporalEval:
    """
    This class help us converting the input into TLINK format and evaluate them using the temporal evaluation tools
    developed by UzZaman. We use the variation of their method that use both the reduced graph and rewarding
    un-inferable implicit relations.

    Reference:
    Interpreting the Temporal Aspects of Language, Naushad UzZaman, 2012
    """

    def __init__(self, doc_id, g2s_mapping, gold_nugget_table, raw_gold_links,
                 sys_nugget_table, raw_sys_links, gold_corefs, sys_corefs):

        # Store how the event nugget ids.
        self.gold_nuggets = []
        self.sys_nuggets = []

        # Stores time ML nodes that actually exists in gold standard and system.
        self.gold_nodes = []
        self.sys_nodes = []

        # Store the mapping from nugget id to unified time ML node id.
        self.system_nugget_to_node = {}
        self.gold_nugget_to_node = {}

        # Store another set of time ML nodes that represents clusters.
        self.cluster_nodes = []
        self.cluster_id_to_node = {}

        self.store_nugget_nodes(gold_nugget_table, sys_nugget_table, g2s_mapping)
        self.gold_clusters, self.gold_cluster_lookup = find_equivalent_sets(gold_corefs, self.gold_nuggets)
        self.sys_clusters, self.sys_cluster_lookup = find_equivalent_sets(sys_corefs, self.sys_nuggets)
        self.store_cluster_nodes(self.gold_clusters)

        gold_links_by_type = propagate_through_equivalence(raw_gold_links, self.gold_clusters, self.gold_cluster_lookup)
        sys_links_by_type = propagate_through_equivalence(raw_sys_links, self.sys_clusters, self.sys_cluster_lookup)

        rewritten_lookup = rewrite_lookup(self.gold_cluster_lookup, g2s_mapping, gold_nugget_table, sys_nugget_table)

        gold_cluster_links = convert_to_cluster_links(gold_links_by_type, self.gold_cluster_lookup)
        sys_cluster_links = convert_to_cluster_links(sys_links_by_type, rewritten_lookup)

        self.possible_types = gold_links_by_type.keys()

        if not Config.no_temporal_validation:
            if not validate(set([nugget[2] for nugget in gold_nugget_table]), gold_links_by_type):
                raise RuntimeError("The gold standard edges cannot form a valid temporal graph.")

            if not validate(set([nugget[2] for nugget in sys_nugget_table]), sys_links_by_type):
                raise RuntimeError("The system edges cannot form a valid temporal graph.")

        self.gold_time_ml = self.make_all_time_ml(convert_links(gold_links_by_type), self.gold_nugget_to_node,
                                                  self.gold_nodes)
        self.sys_time_ml = self.make_all_time_ml(convert_links(sys_links_by_type), self.system_nugget_to_node,
                                                 self.sys_nodes)

        self.gold_cluster_time_ml = self.make_all_time_ml(convert_links(gold_cluster_links), self.cluster_id_to_node,
                                                          self.cluster_nodes)
        self.sys_cluster_time_ml = self.make_all_time_ml(convert_links(sys_cluster_links), self.cluster_id_to_node,
                                                         self.cluster_nodes)

        self.doc_id = doc_id

    def write_time_ml(self):
        """
        Write the TimeML file to disk.
        :return:
        """
        self.write(self.gold_time_ml, Config.temporal_gold_dir)
        self.write(self.sys_time_ml, Config.temporal_sys_dir)

        self.write(self.gold_cluster_time_ml, Config.temporal_gold_dir + "_cluster")
        self.write(self.sys_cluster_time_ml, Config.temporal_sys_dir + "_cluster")

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

    @staticmethod
    def eval_time_ml():
        logger.info("Running TimeML scorer.")

        for link_type in os.listdir(Config.temporal_result_dir):
            # gold_sub_dir = os.path.join(Config.temporal_result_dir, link_type, Config.temporal_gold_dir)
            # sys_sub_dir = os.path.join(Config.temporal_result_dir, link_type, Config.temporal_sys_dir)
            #
            # with open(temporal_output, 'wb', 0) as out_file:
            #     subprocess.call(["python", Config.temp_eval_executable, gold_sub_dir, sys_sub_dir,
            #                      '0', "implicit_in_recall"], stdout=out_file)

            run_eval(link_type, os.path.join(Config.temporal_result_dir, link_type, Config.temporal_out),
                     Config.temporal_gold_dir, Config.temporal_sys_dir)

            # # Evaluate the part using the clustering.
            temporal_output = os.path.join(Config.temporal_result_dir, link_type, Config.temporal_out_cluster)

            # gold_sub_dir = os.path.join(Config.temporal_result_dir, link_type, Config.temporal_gold_dir + "_cluster")
            # sys_sub_dir = os.path.join(Config.temporal_result_dir, link_type, Config.temporal_sys_dir + "_cluster")
            #
            # with open(temporal_output, 'wb', 0) as out_file:
            #     subprocess.call(["python", Config.temp_eval_executable, gold_sub_dir, sys_sub_dir,
            #                      '0', "implicit_in_recall"], stdout=out_file)

            run_eval(link_type, os.path.join(Config.temporal_result_dir, link_type, Config.temporal_out_cluster),
                     Config.temporal_gold_dir + "_cluster", Config.temporal_sys_dir + "_cluster")

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

    def store_cluster_nodes(self, clusters):
        tid = 0

        for cluster_id, cluster in clusters.iteritems():
            node_id = "te%d" % tid
            self.cluster_nodes.append(cluster_id)
            self.cluster_id_to_node[cluster_id] = node_id
            tid += 1

    def store_nugget_nodes(self, gold_nugget_table, sys_nugget_table, m_mapping):
        mapped_system_mentions = set()

        self.gold_nuggets = [nugget[2] for nugget in gold_nugget_table]
        self.sys_nuggets = [nugget[2] for nugget in sys_nugget_table]

        tid = 0
        for gold_index, (system_index, _) in enumerate(m_mapping):
            node_id = "te%d" % tid
            tid += 1

            gold_temporal_instance_id = self.gold_nuggets[gold_index]
            self.gold_nugget_to_node[gold_temporal_instance_id] = node_id
            self.gold_nodes.append(node_id)

            if system_index != -1:
                system_nugget_id = self.sys_nuggets[system_index]
                self.system_nugget_to_node[system_nugget_id] = node_id
                self.sys_nodes.append(node_id)
                mapped_system_mentions.add(system_index)

        for system_index, system_nugget in enumerate(self.sys_nuggets):
            if system_index not in mapped_system_mentions:
                node_id = "te%d" % tid
                tid += 1

                self.system_nugget_to_node[system_nugget] = node_id
                self.sys_nodes.append(node_id)

    def make_all_time_ml(self, links_by_name, normalized_nodes, nodes):
        all_time_ml = {}

        all_links = []

        for name in self.possible_types:
            if name in links_by_name:
                links = links_by_name[name]
                all_time_ml[name] = self.make_time_ml(links, normalized_nodes, nodes)
                all_links.extend(links)
            else:
                all_time_ml[name] = self.make_time_ml([], normalized_nodes, nodes)

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

    @staticmethod
    def create_instance(parent, nodes):
        for node in nodes:
            instance = SubElement(parent, "MAKEINSTANCE")
            instance.set("eiid", "instance_" + node)
            instance.set("eid", node)

    @staticmethod
    def annotate_timeml_events(parent, nodes):
        text = SubElement(parent, "TEXT")
        for tid in nodes:
            make_event(text, tid)

    @staticmethod
    def create_tlinks(time_ml, links, normalized_nodes):
        lid = 0

        unknown_nodes = set()

        for left, right, relation_type in links:
            if left not in normalized_nodes:
                unknown_nodes.add(left)
                continue

            if right not in normalized_nodes:
                unknown_nodes.add(right)
                continue

            normalized_left = normalized_nodes[left]
            normalized_right = normalized_nodes[right]

            link = SubElement(time_ml, "TLINK")
            link.set("lid", "l%d" % lid)
            link.set("relType", relation_type)
            link.set("eventInstanceID", normalized_left)
            link.set("relatedToEventInstance", normalized_right)

        for node in unknown_nodes:
            logger.error("Node %s is not a known node." % node)

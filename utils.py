import logging
import math
import re
import sys
import os
import errno

logger = logging.getLogger(__name__)


def terminate_with_error(msg):
    logger.error(msg)
    logger.error("Scorer terminate with error.")
    sys.exit(1)


def natural_order(key):
    """
    Compare order based on the numeric values in key, for example, 't1 < t2'
    :param key:
    :return:
    """
    if type(key) is int:
        return key
    convert = lambda text: int(text) if text.isdigit() else text
    return [convert(c) for c in re.split('([0-9]+)', key)]


def nan_as_zero(v):
    """
    Treat NaN as zero, should only be used for printing.
    :param v:
    :return:
    """
    return 0 if math.isnan(v) else v


def get_or_else(dictionary, key, value):
    if key in dictionary:
        return dictionary[key]
    else:
        return value


def get_or_terminate(dictionary, key, error_msg):
    if key in dictionary:
        return dictionary[key]
    else:
        terminate_with_error(error_msg)


def check_unique(keys):
    return len(keys) == len(set(keys))


def put_or_increment(table, key, value):
    try:
        table[key] += value
    except KeyError:
        table[key] = value


def transitive_not_resolved(clusters):
    """
    Check whether transitive closure is resolved between clusters.
    :param clusters:
    :return: False if not resolved
    """
    ids = clusters.keys()
    for i in range(0, len(ids) - 1):
        for j in range(i + 1, len(ids)):
            if len(clusters[i].intersection(clusters[j])) != 0:
                logger.error(
                    "Non empty intersection between clusters found. Please resolve transitive closure before submit.")
                logger.error(clusters[i])
                logger.error(clusters[j])
                return True
    return False


def add_to_multi_map(multi_map, key, val):
    """
    Utility class to make the map behave like a multi-map, a key is mapped to multiple values
    :param multi_map: A map to insert to
    :param key:
    :param val:
    :return:
    """
    if key not in multi_map:
        multi_map[key] = []
    multi_map[key].append(val)


def within_cluster_span_duplicate(cluster, event_mention_id_2_sorted_tokens):
    """
    Check whether there is within cluster span duplication, i.e., two mentions in the same cluster have the same span,
    this is not allowed.
    :param cluster: The cluster
    :param event_mention_id_2_sorted_tokens: A map from mention id to span (in terms of tokens)
    :return:
    """
    span_map = {}
    for eid in cluster:
        span = tuple(get_or_terminate(event_mention_id_2_sorted_tokens, eid,
                                      "Cluster contains event that is not in mention list : [%s]" % eid))
        if span in span_map:
            if span is not ():
                logger.error("Span within the same cluster cannot be the same.")
                logger.error("%s->[%s]" % (eid, ",".join(str(x) for x in span)))
                logger.error("%s->[%s]" % (span_map[span], ",".join(str(x) for x in span)))
            return True
        else:
            span_map[span] = eid


def supermakedirs(path, mode=0775):
    """
    A custom makedirs method that get around the umask exception.
    :param path: The path to make directories
    :param mode: The mode of the directory
    :return:
    """
    if not path or os.path.exists(path):
        return []
    (head, tail) = os.path.split(path)
    res = supermakedirs(head, mode)
    os.mkdir(path)
    os.chmod(path, mode)
    res += [path]
    return res


def create_parent_dir(p):
    """
    Create parent directory if not exists.
    :param p: path to file
    :raise:
    """
    try:
        head, tail = os.path.split(p)
        if head != "":
            supermakedirs(head)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


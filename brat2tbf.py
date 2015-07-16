#!/usr/bin/python

"""
    A simple piece of python code that could convert the Brat annotation
tool format into Event Mention Detection format for easy evaluation. For
detailed features and usage please refer to the README file

    Author: Zhengzhong Liu ( liu@cs.cmu.edu )
"""
import argparse
import logging
import sys
import os
import errno

bratSpanMarker = "T"
bratEventMarker = "E"
bratAttMarker = "A"
bratAttMarkerBack = "M"  # for backward compatibility
bratRelationMarker = "R"

outputCommentMarker = "#"
outputBodMarker = "#BeginOfDocument"  # mark begin of a document
outputEodMarker = "#EndOfDocument"  # mark end of a document
outputRelationMarker = "@"  # append before relation
coreference_relation_name = "Coreference"  # mark coreference
coreference_cluster_prefix = "C"

missingAttributePlaceholder = "NOT_ANNOTATED"

text_bounds = {}  # all text bounds
events = {}  # all events
atts = {}  # all attributes
rels = {}  # all relations

out = "converted"
out_ext = ".tbf"  # short for token based format
engine_id = "brat_conversion"
tokenJoiner = ","

# brat_annotation_ext = ".tkn.ann"
# token_offset_ext = ".txt.tab"  # accroding to LDC2014R55

brat_annotation_ext = ".ann"
token_offset_ext = ".tab"  # Simplest extensions

token_offset_fields = [2, 3]

annotation_on_source = False

logger = logging.getLogger()


def main():
    global out
    global out_ext
    global engine_id
    global annotation_on_source
    global token_offset_ext
    global brat_annotation_ext
    global token_offset_fields

    parser_description = (
        "This converter converts Brat annotation files to "
        "one single token based event mention description file (CMU format). "
        "It accepts a single file name or a directory name that contains the "
        "Brat annotation output. The converter also requires token offset "
        "files that shares the same name with the annotation file, with "
        "extension " + token_offset_ext + ". The converter will search for "
                                          "the token file in the directory specified by '-t' argument")

    parser = argparse.ArgumentParser(description=parser_description)
    # required arguments first
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--dir", help="directory of the annotation files")
    group.add_argument("-f", "--file", help="name of one annotation file")
    parser.add_argument(
        "-t", "--tokenPath",
        help="directory to search for the corresponding token files",
        required=True)

    # optional arguments now
    parser.add_argument(
        "-o", "--out",
        help="output path, '" + out + "' in the current path by default")
    parser.add_argument(
        "-oe", "--ext",
        help="output extension, '" + out_ext + "' by default")
    parser.add_argument(
        "-i", "--eid",
        help="an engine id that will appears at each line of the output "
             "file. '" + engine_id + "' will be used by default")
    parser.add_argument(
        "-w", "--overwrite", help="force overwrite existing output file",
        action='store_true')
    parser.add_argument(
        "-of", "--offset_field", help="A pair of integer indicates which column we should "
                                      "read the offset in the token mapping file, index starts"
                                      "at 0, default value will be %s" % token_offset_fields
    )
    parser.add_argument(
        "-te", "--token_table_extension",
        help="any extension appended after docid of token table files. "
             "Default is " + token_offset_ext)
    parser.add_argument(
        "-ae", "--annotation_extension",
        help="any extension appended after docid of annotation files. "
             "Default is " + brat_annotation_ext)
    parser.add_argument(
        "-b", "--debug", help="turn debug mode on", action="store_true")
    parser.set_defaults(debug=False)

    args = parser.parse_args()
    stream_handler = logging.StreamHandler(sys.stderr)
    logger.addHandler(stream_handler)
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter('[%(levelname)s] %(asctime)s : %(message)s'))

    # if args.source:
    # annotation_on_source = True
    # logger.debug("Will use source offsets for tokens")

    if args.tokenPath is not None:
        if not os.path.isdir(args.tokenPath):
            logger.error(
                "Token directory does not exists (or is not a directory) \n\n")
            parser.print_help()
            sys.exit(1)
    else:
        logger.error(
            "Token directory does not exists (or is not a directory) \n\n")
        parser.print_help()
        sys.exit(1)

    if args.token_table_extension is not None:
        token_offset_ext = args.token_table_extension

    if args.annotation_extension is not None:
        brat_annotation_ext = args.annotation_extension

    if args.offset_field is not None:
        try:
            token_offset_fields = [int(x) for x in args.offset_field.split(",")]
        except ValueError as _:
            logger.error("Should provide two integer with comma in between")

    # set default value to optional arguments
    if args.out is not None:
        out = args.out
    if args.ext is not None:
        out_ext = args.ext
    if args.eid is not None:
        engine_id = args.eid

    # ensure output directory exists
    try:
        head, tail = os.path.split(out)
        if head != "":
            os.makedirs(head)
    except OSError:
        (t, v, trace) = sys.exc_info()
        if v.errno != errno.EEXIST:
            raise

    out_path = out + out_ext
    if not args.overwrite and os.path.isfile(out_path):
        logger.error(
            "Output path [%s] already exists, "
            "use '-w' flag to force overwrite" % out_path)
        sys.exit(1)

    out_file = open(out_path, 'w')

    if args.dir is not None:
        # parse directory
        for f in os.listdir(args.dir):
            if f.endswith(brat_annotation_ext):
                parse_annotation_file(
                    os.path.join(args.dir, f), args.tokenPath, out_file)
    elif args.file is not None:
        # parse one annotation file
        if args.file.endswith(brat_annotation_ext):
            parse_annotation_file(args.file, args.tokenPath, out_file)
    else:
        logger.error("No annotations provided\n")


def clear():
    text_bounds.clear()  # all text bounds
    events.clear()  # all events
    atts.clear()  # all attributes
    rels.clear()  # all relations


def join_list(items, joiner):
    sep = ""
    s = ""
    for item in items:
        s += sep
        s += str(item)
        sep = joiner
    return s


def chop(s, begin):
    if s.startswith(begin):
        return s[len(begin):]
    return s


def rchop(s, ending):
    if s.endswith(ending):
        return s[:-len(ending)]
    return s


def parse_annotation_file(file_path, token_dir, of):
    # otherwise use the provided directory to search for it
    basename = os.path.basename(file_path)
    logger.debug("processing " + basename)
    token_path = os.path.join(
        token_dir, basename[:-len(brat_annotation_ext)] + token_offset_ext)

    if os.path.isfile(file_path) and os.path.isfile(token_path):
        f = open(file_path)
        token_file = open(token_path)
        # text_id = os.path.splitext(os.path.basename(f.name))[0]
        text_id = rchop(os.path.basename(f.name), brat_annotation_ext)
        logger.debug("Document id is " + text_id)
        read_all_anno(f)

        # match from text bound to token id
        text_bound_id_2_token_id = get_text_bound_2_token_mapping(token_file)

        eids = events.keys()
        eids.sort(key=lambda x: int(x[1:]))

        # write begin of document
        of.write(outputBodMarker + " " + text_id + "\n")
        # write each mention in a line
        for eid in eids:
            event_type = events[eid][0][0]
            text_bound_id = events[eid][0][1]
            realis_status = missingAttributePlaceholder
            if eid in atts:
                att = atts[eid]
                if "Realis" in att:
                    realis_status = att["Realis"][1]
            text_bound = text_bounds[text_bound_id]
            spans = text_bound[1]
            token_ids = text_bound_id_2_token_id[text_bound_id]
            text = text_bound[2]

            of.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                engine_id, text_id, eid, join_list(token_ids, tokenJoiner),
                text, event_type, realis_status))

        for rel_name, relations in rels.iteritems():
            if rel_name != coreference_relation_name:
                for relation in relations:
                    of.write(
                        "%s%s\t%s\t%s,%s\n" % (
                            outputRelationMarker, rel_name, relation[0], relation[1],
                            relation[2]))
            else:
                logger.debug("Resolving coreference")
                resolved_coref_chains = resolve_transitive_closure(relations)
                for chain in resolved_coref_chains:
                    of.write("%s%s\t%s%s\t%s\n" % (
                        outputRelationMarker, rel_name, coreference_cluster_prefix, chain[0], ",".join(chain[1])))

                    # write end of sentence
        of.write(outputEodMarker + "\n")
    else:
        # the missing file will be skipped but others will still be done
        logger.error(
            "Annotation path %s or token path %s not found. "
            "Will still try to process other annotation files." % (
                file_path, token_path))
    clear()


def transitive_merge(clusters):
    merged_clusters = []

    merged_i = -1
    merged_j = -1

    for i in range(0, len(clusters) - 1):
        for j in range(i + 1, len(clusters)):
            if len(clusters[i].intersection(clusters[j])) != 0:
                union = clusters[i].union(clusters[j])
                # logger.debug("Intersection is ")
                # logger.debug(clusters[i].intersection(clusters[j]))
                # logger.debug("Union is")
                # logger.debug(union)
                # logger.debug("Found merging point")
                merged_clusters.append(union)
                merged_i = i
                merged_j = j
                found = True
                break
        else:
            continue
        break

    # logger.debug(merged_i)

    if merged_i != -1:
        # logger.debug("Now is ")
        # logger.debug(merged_clusters)
        # logger.debug("Add the rest")
        merged_clusters.extend(clusters[: merged_i])
        merged_clusters.extend(clusters[merged_i + 1: merged_j])
        merged_clusters.extend(clusters[merged_j + 1:])
    else:
        merged_clusters.extend(clusters)

    return merged_clusters


def resolve_transitive_closure(coref_relations):
    clusters = []

    for coref_rel in coref_relations:
        mention1 = coref_rel[1]
        mention2 = coref_rel[2]
        for cluster in clusters:
            if mention1 in cluster or mention2 in cluster:
                cluster.add(mention1)
                cluster.add(mention2)
                break
        else:
            new_cluster = {mention1, mention2}
            clusters.append(new_cluster)

    while True:
        merged = transitive_merge(clusters)
        if len(merged) == len(clusters):
            # if no new merges found
            break
        clusters = merged

    # add some cluster id
    clusters_with_id = []
    id = 0
    for cluster in clusters:
        clusters_with_id.append((id, cluster))
        id += 1

    return clusters_with_id


def get_text_bound_2_token_mapping(token_file):
    text_bound_id_2_token_id = {}
    # ignore the header
    # _ = token_file.readline()
    is_first_line = True
    for tokenLine in token_file:
        fields = tokenLine.rstrip().split("\t")
        if len(fields) <= token_offset_fields[1]:
            if is_first_line:
                # The first one might just be a header.
                logger.warning("Ignoring the token file header.")
                continue
            else:
                logger.error("Token files only have %s fields, are you setting "
                             "the correct token offset fields?" % len(fields))
                exit(1)
        is_first_line = False

        # important! we need to make sure that which offsets we are based on

        token_span = (int(fields[token_offset_fields[0]]), int(fields[token_offset_fields[1]]) + 1)

        # if annotation_on_source:
        # token_span = (int(fields[2]), int(fields[3]) + 1)
        # else:
        # token_span = (int(fields[4]), int(fields[5]) + 1)

        # one token maps to multiple text bound is possible
        for text_bound_id in find_corresponding_text_bound(token_span):
            if text_bound_id not in text_bound_id_2_token_id:
                text_bound_id_2_token_id[text_bound_id] = []
            text_bound_id_2_token_id[text_bound_id].append(fields[0])
    return text_bound_id_2_token_id


def find_corresponding_text_bound(token_span):
    text_bound_ids = []
    for text_bound_id, text_bound in text_bounds.iteritems():
        for annSpan in text_bound[1]:
            if covers(annSpan, token_span):
                text_bound_ids.append(text_bound_id)
            elif covers(token_span, annSpan):
                text_bound_ids.append(text_bound_id)
    return text_bound_ids


def covers(covering_span, covered_span):
    if (covering_span[0] <= covered_span[0] and
                covering_span[1] >= covered_span[1]):
        return True
    return False


def parse_span(all_span_str):
    span_strs = all_span_str.split(";")
    spans = []
    for span_str in span_strs:
        span = span_str.split()
        spans.append((int(span[0]), int(span[1])))
    return spans


def parse_text_bound(fields):
    if len(fields) != 3:
        logger.error("Incorrect number of fields in a text bound annotation")
    tid = fields[0]
    type_span = fields[1].split(" ", 1)
    tb_type = type_span[0]
    spans = parse_span(type_span[1])
    text = fields[2]
    return tid, (tb_type, spans, text)


def parse_event(fields):
    eid = fields[0]
    trigger_and_roles = fields[1].split()
    trigger = trigger_and_roles[0].split(":")

    roles = []
    for rolesStr in trigger_and_roles[1:]:
        role = rolesStr.split(":")
        roles.append(role)

    return eid, (trigger, roles)


def parse_attribute(fields):
    aid = fields[0]
    value = fields[1].split()
    att_name = value[0]
    target_id = value[1]
    target_value = True  # binary

    if len(value) == 3:  # multi-valued
        target_value = value[2]

    return aid, target_id, att_name, target_value


def parse_relation(fields):
    """
    Assumes all relation are binary, argument names are discarded
    :param fields: correspond to one Brat line seperated by tab
    :return: relation id, relation name, arg1 and arg2
    """
    rel, a1, a2 = fields[1].split(" ")
    rel_id = fields[0]
    return rel_id, rel, a1.split(":")[1], a2.split(":")[1]


def read_all_anno(f):
    for line in f:
        if line.startswith(outputCommentMarker):
            pass
        fields = line.rstrip().split("\t", 2)
        if line.startswith(bratSpanMarker):
            text_bound = parse_text_bound(fields)
            text_bounds[text_bound[0]] = text_bound[1]
        if line.startswith(bratEventMarker):
            event = parse_event(fields)
            events[event[0]] = event[1]
        if line.startswith(bratAttMarker) or line.startswith(bratAttMarkerBack):
            aid, target_id, att_name, target_value = parse_attribute(fields)
            if target_id in atts:
                atts[target_id][att_name] = (aid, target_value)
            else:
                atts[target_id] = {}
                atts[target_id][att_name] = (aid, target_value)
        if line.startswith(bratRelationMarker):
            rel_id, rel_name, a1, a2 = parse_relation(fields)
            if rel_name not in rels:
                rels[rel_name] = []
            rels[rel_name].append((rel_id, a1, a2))


if __name__ == "__main__":
    main()

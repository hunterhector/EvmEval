#!/usr/bin/python

import sys
import glob
import shutil
import os


def complete_links(src_file):
    result_lines = []

    relations = []
    annotations = []

    for l in src_file:
        l = l.strip()
        result_lines.append(l)

        if l.startswith("R"):
            relations.append(l)
        else:
            annotations.append(l)

    event_to_span, span_to_events = find_same_span(annotations)
    rid = next_available_relation_id(relations)

    span_based_relations = set()

    event_based_relations = set()

    for line in relations:
        fields = line.split("\t")
        if line.startswith("R"):
            r_content = fields[1].split(" ")
            if r_content[0] == "After" or r_content[0] == "Subevent":
                arg1 = r_content[1].split(":")[1]
                arg2 = r_content[2].split(":")[1]

                arg1_span = event_to_span[arg1]
                arg2_span = event_to_span[arg2]

                span_based_relations.add((r_content[0], arg1_span, arg2_span))
                event_based_relations.add((r_content[0], arg1, arg2))

    for t, span1, span2 in span_based_relations:
        # print span1, span2
        for event1 in span_to_events[span1]:
            for event2 in span_to_events[span2]:
                if (t, event1, event2) not in event_based_relations:
                    new_line = "R%d\t%s Arg1:%s Arg2:%s" % (rid, t, event1, event2)
                    print "Adding new line: %s to file %s." % (new_line, basename)
                    result_lines.append(new_line)

    return result_lines


def next_available_relation_id(relations):
    max_id = -1
    for r in relations:
        rid = int(r.split("\t")[0][1:])
        if rid > max_id:
            max_id = rid
    return max_id + 1


def find_same_span(lines):
    tid_to_span = {}
    event_to_span = {}
    span_to_event = {}

    for line in lines:
        fields = line.split("\t")
        if line.startswith("T"):
            span = tuple(fields[1].split()[1:])
            tid_to_span[fields[0]] = span

    for line in lines:
        fields = line.split("\t")
        if line.startswith("E"):
            eid = fields[0]
            span = tid_to_span[fields[1].split(":")[1]]

            event_to_span[eid] = span

            try:
                span_to_event[span].append(eid)
            except KeyError:
                span_to_event[span] = [eid]

    return event_to_span, span_to_event


if len(sys.argv) != 3:
    print "Usage: python after_link_completion.py [Brat Annotation Directory] [Output Directory]"
    sys.exit(1)

input_dir = sys.argv[1]
output_dir = sys.argv[2]

if os.path.exists(input_dir) and not os.path.exists(output_dir):
    os.makedirs(output_dir)

for f in glob.glob(os.path.join(input_dir, "*.txt")):
    basename = os.path.basename(f)
    target_path = os.path.join(output_dir, basename)
    shutil.copy(f, target_path)

for f in glob.glob(os.path.join(input_dir, "*.ann")):
    basename = os.path.basename(f)
    target_path = os.path.join(output_dir, basename)
    with open(f) as anno_file, open(target_path, 'w') as out_file:
        result_lines = complete_links(anno_file)
        out_file.write("\n".join(result_lines))

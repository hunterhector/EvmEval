#!/usr/bin/python

"""
Convert a token based tbf file to character based tbf file.
"""
import argparse
import logging
import os
import re
import errno

token_offset_fields = [2, 3]
logger = logging.getLogger()
token_suffix = ".tab"

inner_span_joiner = ","
inter_span_joiner = ";"


def main():
    parser = argparse.ArgumentParser(description="Convert between token based and character based tbf format.")
    parser.add_argument("-t", "--token_dir", help="The directory to find token files.", required=True)
    parser.add_argument("-s", "--source", help="Source tbf path.", required=True)
    parser.add_argument("-o", "--output", help="Output tbf path.", required=True)
    parser.add_argument("-m", "--mode", choices=["2char", "2token"], help="Conversion mode, to character or to token.",
                        required=True)

    args = parser.parse_args()

    convert_func = token_2_char if args.mode == "2char" else char_2_token

    if not os.path.exists(os.path.dirname(args.output)):
        try:
            os.makedirs(os.path.dirname(args.output))
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise

    with open(args.source) as source, open(args.output, 'w') as output:
        for line in source:
            if line.startswith("#BeginOfDocument"):
                docid = line.split()[1]
                token_id_2_span = parse_token_file(os.path.join(args.token_dir, docid + token_suffix))
                output.write(line)
                continue

            fields = line.split("\t")
            if len(fields) >= 7:
                span = fields[3]
                converted_span = convert_func(span, token_id_2_span)
                fields[3] = converted_span
                output.write("\t".join(fields))
            else:
                output.write(line)

# Check here? probably not correct.
def char_2_token(char_span_str, token_id_2_span):
    ids = []
    for char_span in char_span_str.split(inter_span_joiner):
        for tid, tspan in token_id_2_span.iteritems():
            if covers(char_span, tspan):
                ids.append(tid)
    return inner_span_joiner.join(ids)


def token_2_char(token_id_str, token_id_2_span):
    convert = lambda text: int(text) if text.isdigit() else text

    char_spans = []
    span_start = -1
    span_end = -1
    last_id = -1

    for tid in sorted(token_id_str.split(inner_span_joiner), key=natural_order):
        nid = convert(tid)
        token_begin = token_id_2_span[tid][0]
        token_end = token_id_2_span[tid][1]
        if last_id == -1:
            # First token case.
            span_start = token_begin
            span_end = token_end
            last_id = nid
        elif last_id == nid - 1:
            # Continuous case.
            span_end = token_end
            last_id = nid
        else:
            # Discontinuous case.
            char_spans.append(str(span_start) + inner_span_joiner + str(span_end))
            span_start = -1
            span_end = -1
            last_id = -1

    char_spans.append(str(span_start) + inner_span_joiner + str(span_end))

    return inter_span_joiner.join(char_spans)


def parse_token_file(token_file_path):
    token_id_2_span = {}

    is_first_line = True
    for token_line in open(token_file_path):
        # We assume no whitespaces within fields.
        fields = token_line.rstrip().split("\t")
        if len(fields) <= token_offset_fields[1]:
            if is_first_line:
                # The first one might just be a header.
                logger.info("Ignoring the token file header.")
            else:
                logger.error("Token files only have %s fields, are you setting "
                             "the correct token offset fields?" % len(fields))
                exit(1)
        is_first_line = False

        # Important! we need to make sure that which offsets we are based on.
        token_span = (int(fields[token_offset_fields[0]]), int(fields[token_offset_fields[1]]))

        token_id_2_span[fields[0]] = token_span

    return token_id_2_span


def covers(covering_span, covered_span):
    if covering_span[0] <= covered_span[0] and covering_span[1] >= covered_span[1]:
        return True
    return False


def natural_order(key):
    convert = lambda text: int(text) if text.isdigit() else text
    return [convert(c) for c in re.split('([0-9]+)', key)]


if __name__ == "__main__":
    main()

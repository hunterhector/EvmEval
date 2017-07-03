#!/usr/bin/python

import sys
import os

brat_annotation_ext = ".ann"


def get_span(span_str):
    spans = span_str.split(";")

    begin = -1
    end = -1

    for span in spans:
        lr = span.split()
        if begin == -1:
            begin = int(lr[0])
        span_end = int(lr[1])
        if span_end > end:
            end = span_end

    return begin, end


def write_file(input_dir, output_file):
    with open(output_file, 'w') as out:
        for f in os.listdir(input_dir):
            if f.endswith(brat_annotation_ext):
                basename = f.replace(brat_annotation_ext, "")
                with open(os.path.join(input_dir, f)) as ann:
                    for line in ann.readlines():
                        parts = line.split("\t")
                        if len(parts) > 1:
                            anno = parts[1]

                            anno_parts = anno.split(" ",1)

                            if anno_parts[0] == "Unannotated":
                                begin, end = get_span(anno_parts[1])
                                out.write("%s\t%d\t%d\n" % (basename, begin, end))


if __name__ == '__main__':
    if not len(sys.argv) == 3:
        print "USage: this [input dir] [output file]"

    write_file(sys.argv[1], sys.argv[2])

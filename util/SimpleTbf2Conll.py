#!/usr/bin/python

"""
A simple TBF to CoNLL converter that convert only the mention text.
"""

import sys
import re
from itertools import groupby

if len(sys.argv) < 3:
    print "Usage : SimpleTbf2Conll.py [tbf input] [conll output]"

tbf_in = sys.argv[1]
conll_out = sys.argv[2]


def natural_order(key):
    """
    Compare order based on the numeric values in key, for example, 't1 < t2'
    :param key:
    :return:
    """
    convert = lambda text: int(text) if text.isdigit() else text
    return [convert(c) for c in re.split('([0-9]+)', key)]


def header_change(tbf_header):
    id = tbf_header.split()[1]
    return "#begin document (%s); part 000\n" % id


def footer_change():
    return "#end document\n"


def text_change(tbf_text):
    parts = tbf_text.split("\t")
    if len(parts) >= 4:
        token_ids = parts[3].split(",")
        tokens = parts[4].split(" ")
        return [(i, "%s\t%s\t%s\t\n" % (parts[1], i, t)) for i, t in zip(token_ids, tokens)]
    else:
        return []


with open(tbf_in) as tbf, open(conll_out, 'w') as conll:
    conll_lines = []
    for line in tbf:
        line = line.strip()
        if line.startswith("#BeginOfDocument"):
            conll_header = header_change(line)
            conll.write(conll_header)
        elif line.startswith("#EndOfDocument"):
            sorted_lines = sorted(conll_lines, key=lambda tup: natural_order(tup[0]))
            unique_lines = [e for e, _ in groupby(sorted_lines)]
            conll.writelines(zip(*unique_lines)[1])
            conll.write(footer_change())
            conll_lines = []
        else:
            conll_lines.extend(text_change(line))

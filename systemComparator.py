#!/usr/bin/python 

"""
    Combine output from multiple systems and compare them
"""

import argparse
import logging
import sys
import os
import errno

spanMarker = "T"
eventMarker = "E"
attMarker = "A"
attMarkerBack = "M" # for backward compatibility
noteMarker = "#"
bodMarker = "#BeginOfDocument" #mark begin of a document
eodMarker = "#EndOfDocument" #mark end of a document

missingAttributePlaceholder = "NOT_ANNOTATED"

textBounds = {} # all text bounds
events = {} # all events
atts = {} # all attributes

out = "converted"
outExt = "tbf" #short for token based format
engineId = "Merged"
tokenJoiner = ","

bratAnnotationExt = ".ann"
tokenOffsetExt = ".tkn"

logger = logging.getLogger()

def main():
    global out
    global outExt
    global engineId

    parser = argparse.ArgumentParser(description="A merger that combine and compare multiple system output"+tokenOffsetExt)
    parser.add_argument("-d","--dir",help="Directory of the files to merge")
    parser.add_argument("-o","--out",help="output path, '"+out+"' by default")
    parser.add_argument("-e","--ext",help="output extension (also the input extension), '"+outExt+"' by default")
    parser.add_argument("-i","--eid",help="an engine id that will appears at each line of the output file")

    args = parser.parse_args()
    stream_handler = logging.StreamHandler(sys.stderr)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.DEBUG)

    if args.out != None:
        out = args.out
    if args.ext != None:
        outExt = args.ext
    if args.eid != None:
        engineId = args.eid

    #ensure output directory exists

    try:
        head,tail = os.path.split(out)
        if head != "":
            os.makedirs(head)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    outFile = open(out+"."+outExt,'w')

    #start to merge

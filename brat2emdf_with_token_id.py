#!/usr/bin/python 

"""
    A simple piece of python code that could convert the Brat annotation
tool format into Event Mention Detection format for easy evaluation. For
detailed features and usage please refer to the README file
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

textBounds = {} # all text bounds
events = {} # all events 
atts = {} # all attributes 

out = "converted"
outExt = "emdf"
engineId = "brat_conversion"
tokenJoiner = ","

bratAnnotationExt = ".ann"
tokenOffsetExt = ".tkn"

logger = logging.getLogger()

def main():
    global out
    global outExt
    global engineId

    parser = argparse.ArgumentParser(description="The converter that convert from Brat to EMDF (CMU format) , requires at least the input file name/directory/list, which contains the Brat annotation, it also requires a token offset file that uses the same name as the annotation file, with extension "+tokenOffsetExt)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d","--dir",help="directory of the annotations")
    group.add_argument("-f","--file",help="name of one annotation file")
    group.add_argument("-l","--filelist",help="a file that each line is a file that will be processed")
    parser.add_argument("-o","--out",help="output path, '"+out+"' by default")
    parser.add_argument("-e","--ext",help="output extension, '"+outExt+"' by default")
    parser.add_argument("-i","--eid",help="an engine id that will appears at each line of the output file")

    args = parser.parse_args() 
    stream_handler = logging.StreamHandler(sys.stderr)  
    logger.addHandler(stream_handler)  

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

    if args.dir != None:
        #parse directory
        for f in os.listdir(args.dir):
            if f.endswith(bratAnnotationExt):
                parse_annotation_file(args.dir+os.sep+f,outFile)
    elif args.file != None:
        #parse one annotation file
        if args.file.endswith(bratAnnotationExt):
            parse_annotation_file(args.file,outFile)
    elif args.filelist != None:
        #parse the filelist
        lst = open(args.filelist)
        for line in lst:
            l = line.rstrip()
            parse_annotation_file(l,outFile)

def clear():
    textBounds = {} # all text bounds
    events = {} # all events 
    atts = {} # all attributes 

def joinList(items,joiner):
    sep = ""
    s = ""
    for item in items:
        s += sep
        s += str(item) 
        sep = joiner 
    return s

def parse_annotation_file(filePath,of):
    tokenPath = filePath[:-len(bratAnnotationExt)]+tokenOffsetExt

    if os.path.isfile(filePath) and os.path.isfile(tokenPath):
        f = open(filePath)
        tokenFile = open(tokenPath)
        textId = os.path.splitext(os.path.basename(f.name))[0]
        read_all_anno(f)
        
        #match from text bound to token id 
        textBoundId2TokenId = getTextBound2TokenMapping(tokenFile)

        eids = events.keys()
        eids.sort(key=lambda x: int(x[1:]) )

        of.write(bodMarker+" "+textId+"\n")
        for eid in eids:
            eventType = events[eid][0][0]
            textBoundId = events[eid][0][1]
            att = atts[eid]
            textBound  = textBounds[textBoundId]
            spans = textBound[1]
            tokenIds = textBoundId2TokenId[textBoundId]
            text = textBound[2]

            of.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n"%(engineId,textId,eid,joinList(tokenIds,tokenJoiner),text,eventType,att["Realis"][1],1))
        of.write(eodMarker+"\n")
        clear()
    else:
        logger.error("Both annotation path %s and token path %s must be given."%(filePath,tokenPath))

def getTextBound2TokenMapping(tokenFile):
    textBoundId2TokenId = {}
    for tokenLine in tokenFile:
        fields = tokenLine.rstrip().split(" ")
        if len(fields) != 4:
            continue
        tokenSpan = (int(fields[2]),int(fields[3]))
        texBoundId = findCoverByTextBound(tokenSpan)
        if texBoundId != -1:
            if not textBoundId2TokenId.has_key(texBoundId):
                textBoundId2TokenId[texBoundId] = []
            textBoundId2TokenId[texBoundId].append(fields[0])
    return textBoundId2TokenId

def findCoverByTextBound(tokenSpan):
        for textBoundId,textBound in textBounds.iteritems():
            for annSpan in textBound[1]:
                if covers(annSpan,tokenSpan):
                    return textBoundId
        return -1

def covers(coveringSpan, coveredSpan):
    if coveringSpan[0] <= coveredSpan[0] and coveringSpan[1] >= coveredSpan[1]:
        return True
    return False

def parse_span(allSpanStr):
    spanStrs = allSpanStr.split(";")
    spans = []
    for spanStr in spanStrs:
        span = spanStr.split()
        spans.append((int(span[0]),int(span[1])))
    return spans

def parse_text_bound(fields):
    if len(fields) != 3:
        logger.error("Incorrect number of fields in a text bound annotation")
    tid = fields[0]
    typeSpan = fields[1].split(" ",1)
    tbType = typeSpan[0]
    spans = parse_span(typeSpan[1])
    text = fields[2]
    return (tid,(tbType,spans,text))

def parse_event(fields):
    eid = fields[0]
    triggerAndRoles = fields[1].split()
    trigger = triggerAndRoles[0].split(":")
    
    roles = []
    for rolesStr in triggerAndRoles[1:]:
        role = rolesStr.split(":")
        roles.append(role)

    return (eid,(trigger,roles))

def parse_attribute(fields):
    aid = fields[0]
    value = fields[1].split()
    attName = value[0]
    targetId = value[1]
    targetValue = True #binary

    if len(value) == 3: #multi-valued
        targetValue = value[2]

    return (aid,targetId,attName,targetValue)

def read_all_anno(f):
    for line in f:
        if line.startswith(noteMarker):
            pass
        fields = line.rstrip().split("\t",2)
        if line.startswith(spanMarker):
            textBound = parse_text_bound(fields)
            textBounds[textBound[0]] = textBound[1]
        if line.startswith(eventMarker):
            event = parse_event(fields)
            events[event[0]]= event[1]
        if line.startswith(attMarker) or line.startswith(attMarkerBack):
            (aid, targetId, attName, targetValue) = parse_attribute(fields) 
            if atts.has_key(targetId):
                atts[targetId][attName] = (aid,targetValue)
            else:
                atts[targetId] = {}
                atts[targetId][attName] = (aid,targetValue)

if __name__ == "__main__":
    main()

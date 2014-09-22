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

missingAttributePlaceholder = "NOT_ANNOTATED"

textBounds = {} # all text bounds
events = {} # all events 
atts = {} # all attributes 

out = "converted"
outExt = "tbf" #short for token based format
engineId = "brat_conversion"
tokenJoiner = ","

bratAnnotationExt = ".ann"
tokenOffsetExt = ".txt.tab" #accroding to LDC2014R55_DEFT_Event_Mention_Detection_Pilot_Tokenized_Data

annotation_on_source = False

logger = logging.getLogger()

def main():
    global out
    global outExt
    global engineId
    global annotation_on_source

    parser = argparse.ArgumentParser(description="This converter converts Brat annotation files to one single token based event mention description file (CMU format). It accepts a single file name or a directory name that contains the Brat annotation output. The converter also requires token offset files that shares the same name with the annotation file, with extension "+tokenOffsetExt + ". The converter will search for the token file in the directory specified by '-t' argument")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d","--dir",help="directory of the annotation files")
    group.add_argument("-f","--file",help="name of one annotation file")
    #group.add_argument("-l","--filelist",help="a file that each line is a file that will be processed")   
    parser.add_argument("-t","--tokenPath",help="directory to search for the corresponding token files",required = True)
    parser.add_argument("-o","--out",help="output path, '"+out+"' in the current path by default")
    parser.add_argument("-e","--ext",help="output extension, '"+outExt+"' by default")
    parser.add_argument("-i","--eid",help="an engine id that will appears at each line of the output file")
    parser.add_argument("-w","--overwrite",help="force overwrite existing output file", action='store_true')
    parser.add_argument("-s","--source",help="true if the annotations are done on source data, default is false", action='store_true')
    parser.set_defaults(source=False)
    parser.add_argument("-b", "--debug",help="turn debug mode on", action="store_true")
    parser.set_defaults(debug=False)

    args = parser.parse_args() 
    stream_handler = logging.StreamHandler(sys.stderr)  
    logger.addHandler(stream_handler)
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if args.source:
        annotation_on_source = True
        logger.debug("Will use source offsets for tokens")

    if args.tokenPath != None:
        if not os.path.isdir(args.tokenPath):
            logger.error("Token directory does not exists (or is not a directory) \n\n")
            parser.print_help()
            sys.exit(1)
    else:
        logger.error("Token directory does not exists (or is not a directory) \n\n")
        parser.print_help()
        sys.exit(1)

    #set default value to optional arguments
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
    except (OSError):
        (t,v,trace) = sys.exc_info()
        if v.errno != errno.EEXIST:
            raise

    outPath = out+"."+outExt
    if not args.overwrite and os.path.isfile(outPath):
        logger.error("Output path [%s] already exists, use '-w' flag to force overwrite"%(outPath))
        sys.exit(1)
        
    outFile = open(outPath,'w')

    if args.dir != None:
        #parse directory
        for f in os.listdir(args.dir):
            if f.endswith(bratAnnotationExt):
                parse_annotation_file(os.path.join(args.dir,f),args.tokenPath,outFile)
    elif args.file != None:
        #parse one annotation file
        if args.file.endswith(bratAnnotationExt):
            basename = os.path.basename(args.file)
            parse_annotation_file(args.file, args.tokenPath,outFile)
#    elif args.filelist != None:
#        #parse the filelist
#        lst = open(args.filelist)
#        for line in lst:
#            l = line.rstrip()
#            if l.endswith(bratAnnotationExt): 
#                basename = os.path.basename(l)
#                parse_annotation_file(l,args.tokenPath,outFile)
    else:
        logger.error("No annotations provided\n")

def clear():
    textBounds.clear() # all text bounds
    events.clear() # all events 
    atts.clear() # all attributes 

def joinList(items,joiner):
    sep = ""
    s = ""
    for item in items:
        s += sep
        s += str(item) 
        sep = joiner 
    return s

def parse_annotation_file(filePath,tokenDir,of):
    #otherwise use the provided directory to search for it 
    basename = os.path.basename(filePath)
    tokenPath = os.path.join(tokenDir,basename[:-len(bratAnnotationExt)]+tokenOffsetExt)

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
            realisStatus = missingAttributePlaceholder
            if eid in atts:
                att = atts[eid]
                if "Realis" in att:
                    realisStatus = att["Realis"][1]
            textBound  = textBounds[textBoundId]
            spans = textBound[1]
            tokenIds = textBoundId2TokenId[textBoundId]
            text = textBound[2]

            of.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n"%(engineId,textId,eid,joinList(tokenIds,tokenJoiner),text,eventType,realisStatus,1))
        of.write(eodMarker+"\n")
    else:
        #the missing file will be skipped but others will still be done
        logger.error("Annotation path %s or token path %s not found. Will still try to process other annotation files"%(filePath,tokenPath))
    clear()

def getTextBound2TokenMapping(tokenFile):
    textBoundId2TokenId = {}
    #ignore the header
    header = tokenFile.readline()
    for tokenLine in tokenFile:
        fields = tokenLine.rstrip().split("\t")
        if len(fields) != 6:
            continue
        #important! we need to make sure that what we are evaluating on
        tokenSpan = None
        if annotation_on_source:
            tokenSpan = (int(fields[2]),int(fields[3]))
        else:
            tokenSpan = (int(fields[4]),int(fields[5]))
        
        #one token maps to multiple text bound is possible
        for textBoundId in findCorrespondingTextBound(tokenSpan):
            if not textBoundId2TokenId.has_key(textBoundId):
                textBoundId2TokenId[textBoundId] = []
            textBoundId2TokenId[textBoundId].append(fields[0])
    return textBoundId2TokenId

def findCorrespondingTextBound(tokenSpan):
        textBoundIds = []
        for textBoundId,textBound in textBounds.iteritems():
            for annSpan in textBound[1]:
                if covers(annSpan,tokenSpan):
                    textBoundIds.append(textBoundId)
                elif covers(tokenSpan,annSpan):
                    textBoundIds.append(textBoundId)

        return textBoundIds

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

#!/usr/bin/python 

"""
    A simple scorer that reads the CMU Event Mention Detection Format 
    data and produce F-Scores
"""
import math
import argparse
import logging
import sys
import os
from itertools import izip

commentMarker = "#"
bodMarker = "#BeginOfDocument" #mark begin of a document 
eodMarker = "#EndOfDocument" #mark end of a document

logger = logging.getLogger()

invisible_words = set(['the','a','an','I','you','he','she','we','they','it','his','her','my','your','mine','yours','our','ours','who','what','where','when','that'])

gf = None
sf = None

docScores = []

spanSeperator = ";"
spanJoiner = "_"

def main():
    global gf
    global sf
    parser = argparse.ArgumentParser(description="Event mention scorer")
    parser.add_argument("-g","--gold",help="Golden Standard",required=True)
    parser.add_argument("-s","--system",help="System output",required=True)
    parser.add_argument("-o","--output",help="Optional evaluation result redirects")

    args = parser.parse_args()
    
    stream_handler=None 
    if args.output != None:   
        evalOut = open(args.out)
        stream_handler = logging.StreamHandler(args.out)
    else:
        stream_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.DEBUG)

    if os.path.isfile(args.gold):
        gf = open(args.gold)
    else:
        logger.error("Cannot find gold standard file at "+gold)
        system.exit(1)
    if os.path.isfile(args.system):
        sf = open(args.system)
    else:
        logger.error("Cannot find system file at "+ system)
        system.exit(1)
  
    while True:
        res = evaluate()
        if not res:
            break

    totalTp = 0
    totalFp = 0
    totalFn = 0
    totalPrec = 0
    totalRecall = 0
    validDocs = 0

    logger.info("========Document results==========")
    for (tp,fp,fn,docId) in docScores:
        prec = tp/(tp+fp) if tp + fp > 0 else float('nan')
        recall = tp/(tp+fn) if tp + fn > 0 else float('nan')
        logger.info("TP\tFP\tFN\tPrec\tRecall\tDoc Id")
        logger.info("%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%s"%(tp,fp,fn,prec,recall,docId))
        
        if math.isnan(prec) or math.isnan(recall):
            #no mentions annotated, treat as invalid file 
            pass
        else:
            validDocs += 1
            totalTp += tp
            totalFp += fp 
            totalFn += fn
            totalPrec += prec 
            totalRecall += recall

    logger.info("\n=======Final Results=========")
    microPrec = totalTp/(totalTp+totalFp) if totalTp+ totalFp > 0 else float('nan')
    microRecall = totalTp/(totalTp+totalFn) if totalTp + totalFn > 0 else float('nan')
    microF1 = 2*microPrec*microRecall/(microPrec+microRecall)

    macroPrec = totalPrec/validDocs if validDocs > 0 else float('nan')
    macroRecall = totalRecall/validDocs if validDocs > 0 else float('nan')
    macroF1 = 2*macroPrec*macroRecall/(macroPrec+macroRecall)

    logger.info("Precision (Micro Average): %.4f",microPrec)
    logger.info("Recall (Micro Average):%.4f",microRecall)
    logger.info("F1 (Micro Average):%.4f",microF1)
    
    logger.info("Precision (Macro Average): %.4f", macroPrec)
    logger.info("Recall (Macro Average): %.4f", macroRecall)
    logger.info("F1 (Macro Average): %.4f", macroF1)

def getNextDoc():
    gLines = []
    sLines = []

    gdocId = ""

    while True:
        line = gf.readline().strip().rstrip()
        if not line:
            break
        if line == eodMarker:
            break
        if line.startswith(commentMarker):
            if line.startswith(bodMarker):
                gdocId = line[len(bodMarker):].strip() 
        elif line == "":
            pass
        else:
            gLines.append(line)

    sdocId = ""
    while True:
        line = sf.readline().rstrip()
        if not line:
            break
        if line == eodMarker:
            break
        if line.startswith(commentMarker):
            if line.startswith(bodMarker):
                sdocId = line[len(bodMarker):].strip()
        elif line == "":
            pass
        else:
            sLines.append(line)

    if gdocId != sdocId:
        logger.error("System document IDs are not aligned with gold standard IDs")
        system.exit(1)
    return (gLines,sLines,gdocId)
    
def parseSpans(s):
    spanStrs = s.split(spanSeperator)
    spans = []
    for spanStrs in spanStrs:
        span = list(map(int,spanStrs.split(spanJoiner)))
        spans.append(span)
    return spans

def parseLine(l):
    '''
    Currently assuming we are using EMDF format suggested by Ed
    '''
    fields = l.split("\t")
    if (len(fields) != 8):
        logger.error("Output are not correctly formatted")
    evmText = fields[4]
    spans = parseSpans(fields[3])

    return (spans,evmText)

def validateSpans(spans):
    lastEnd = -1
    for span in spans:
        if len(span) == 2 and span[1] > span[0]:
            pass
        else:
            logger.error(span+" is not a valid span")    
            system.exit(1)
        if span[0] < lastEnd:
            logger.error("Spans cannot overlaps")
            system.exit(1)

def spanOverlap(span1, span2):
    '''
    return the number of characters that overlaps
    '''
    if span1[1] > span2[0] and span1[0] < span2[1]:
        #find left end 
        leftEnd = span1[0] if span1[0] < span2[0] else span2[0]
        #find right end 
        rightEnd = span1[1] if span1[1] > span2[1] else span2[1]
        return rightEnd - leftEnd
    else:
        #no overlap 
        return 0

def computeOverlapScore(gSpans,sSpans,gEvm,sEvm):
    #validate system span 
    validateSpans(sSpans)

    #character based method has a lot of problems
    gLength = len(gEvm)
    sLength = len(sEvm)
    
    totalOverlap = 0.0
    for gSpan in gSpans:
        for sSpan in sSpans:
            totalOverlap += spanOverlap(gSpan,sSpan)
 
    deno = gLength if gLength < sLength else sLength

    return totalOverlap/deno

def evaluate():
    (gLines,sLines,docId) = getNextDoc()
    
    if not gLines:
        return False

    tp = 0.0
    fp = 0.0
    fn = 0.0

    scoreSlots = [0.0]*len(gLines)
    
    for sl in sLines:
        largestOverlap = -1.0
        (sSpans, sEvm) = parseLine(sl)
        corresGEvm = None

        for index, gl in enumerate(gLines):
            (gSpans, gEvm) = parseLine(gl)
            overlap = computeOverlapScore(gSpans,sSpans,gEvm,sEvm)
            if (overlap > largestOverlap):
                largestOverlap = overlap
                corresGEvm = (gSpans,gEvm,index)

        if largestOverlap > 0:
            corresIndex = corresGEvm[2]
            if largestOverlap > scoreSlots[corresIndex]:
                scoreSlots[corresIndex] = largestOverlap
        else:
            #case where no mapping are found
            fn += 1
            
    for score in scoreSlots:
        if score > 0:
            tp += score 
        else:
            fp += 1

    docScores.append((tp,fp,fn,docId))
    return True
    
if __name__ == "__main__":
    main()

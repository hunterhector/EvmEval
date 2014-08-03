#!/usr/bin/python 

"""
    A simple scorer that reads the CMU Event Mention Detection Format 
    data and produce F-Scores
"""
import math
import errno
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
tokenDir = "."

docScores = []

tokenJoiner = ","
tokenFileExt = ".tkn"

def main():
    global gf
    global sf
    global tokenDir
    parser = argparse.ArgumentParser(description="Event mention scorer")
    parser.add_argument("-g","--gold",help="Golden Standard",required=True)
    parser.add_argument("-s","--system",help="System output",required=True)
    parser.add_argument("-o","--output",help="Optional evaluation result redirects")
    parser.add_argument("-t","--token",help="Path to the directory containing the tokens, will use current directory if not specified")
    args = parser.parse_args()
    
    stream_handler=None 
    if args.output is not None:   
        outPath = args.output
        try:
            head,tail = os.path.split(outPath)
            if head != "":
                os.makedirs(head)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        evalOut = open(outPath,'w')
        stream_handler = logging.StreamHandler(evalOut)
    else:
        stream_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.DEBUG)

    if os.path.isfile(args.gold):
        gf = open(args.gold)
    else:
        logger.error("Cannot find gold standard file at "+args.gold)
        sys.exit(1)
    if os.path.isfile(args.system):
        sf = open(args.system)
    else:
        logger.error("Cannot find system file at "+ args.system)
        sys.exit(1)
  
    if args.token is not None:
        if os.path.isdir(args.token):
            logger.error("Will search token files in "+args.token)
            tokenDir = args.token 
        else:
            logger.error("Cannot find given token directory at " +args.token+", will try search for currrent directory")

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
    microF1 = 2*microPrec*microRecall/(microPrec+microRecall) if microPrec+microRecall > 0 else float('nan')

    macroPrec = totalPrec/validDocs if validDocs > 0 else float('nan')
    macroRecall = totalRecall/validDocs if validDocs > 0 else float('nan')
    macroF1 = 2*macroPrec*macroRecall/(macroPrec+macroRecall) if macroPrec+macroRecall > 0 else float('nan')

    logger.info("Precision (Micro Average): %.4f",microPrec)
    logger.info("Recall (Micro Average):%.4f",microRecall)
    logger.info("F1 (Micro Average):%.4f",microF1)
    
    logger.info("Precision (Macro Average): %.4f", macroPrec)
    logger.info("Recall (Macro Average): %.4f", macroRecall)
    logger.info("F1 (Macro Average): %.4f", macroF1)

def getInvisibleWordIDs(gFileName):
    invisibleIds = set()
    tokenFile = None
    try:
        tokenFile = open(os.path.join(tokenDir,gFileName+tokenFileExt))

        for tline in tokenFile:
            fields = tline.rstrip().split(" ")
            if len(fields) != 4:
                continue 
            if fields[1].lower().strip().rstrip() in invisible_words:
                invisibleIds.add(int(fields[0]))
                logger.debug("Token %s-%s is invisible"%(fields[0],fields[1]))

    except IOError:
        logger.debug("Cannot find token file for doc [%s], will use empty invisible words list"%gFileName)
        pass

    return invisibleIds

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
        sys.exit(1)
    return (gLines,sLines,gdocId)
    
def parseTokenIds(s,invisibleIds):
    tokenStrs = s.split(tokenJoiner)
    tokenIds = set()
    for tokenStr in tokenStrs:
        tokenId = int(tokenStr)
        if not tokenId in invisibleIds:
            tokenIds.add(tokenId)
        else:
            logger.debug("Token Id %d is filtered"%(tokenId))
            pass

    return tokenIds

def parseLine(l,invisibleIds):
    '''
    parse the line, get the token ids, remove invisible ones
    '''
    fields = l.split("\t")
    if (len(fields) != 8):
        logger.error("Output are not correctly formatted")
    tokenIds = parseTokenIds(fields[3],invisibleIds)
    return (tokenIds)

def computeOverlapScore(gTokens,sTokens):
    totalOverlap = 0.0
    
    for sToken in sTokens:
        if sToken in gTokens:
            totalOverlap += 1

    gLength = len(gTokens)
    sLength = len(sTokens)

    deno = gLength if gLength < sLength else sLength

    return totalOverlap/deno

def evaluate():
    (gLines,sLines,docId) = getNextDoc()
   
    if not gLines:
        return False

    invisibleIds = getInvisibleWordIDs(docId)

    tp = 0.0
    fp = 0.0
    fn = 0.0

    #maintaining the score at slot i
    scoreSlots = [0.0]*len(gLines)
    #maininting the actual mapping from gold to system
    mappingSlots = [-1]*len(gLines)
    #maintaining all scores of system mappings to gold
    systemMappingSlots = []*len(sLines)

    for systemIndex, sl in enumerate(sLines):
        largestOverlap = -1.0
        sTokens = parseLine(sl,invisibleIds)
        corresIndex = -1

        for index, gl in enumerate(gLines):
            gTokens = parseLine(gl,invisibleIds)
            overlap = computeOverlapScore(gTokens,sTokens)

            if (overlap > 0):
                #maintaining a max heap based on overlap score
                heappush(systemMappingSlots[systemIndex],(-overlap,systemIndex))

            if (overlap > largestOverlap):
                largestOverlap = overlap
                corresIndex = index

        if largestOverlap > 0:
            if largestOverlap > scoreSlots[corresIndex]:
                scoreSlots[corresIndex] = largestOverlap
                #could consider implementing something that move the previous
                #mapped system score to its second best system mapping
        else:
            #case where no mapping are found
            fp += 1
            
    for score in scoreSlots:
        if score > 0:
            tp += score 
        else:
            fn += 1

    docScores.append((tp,fp,fn,docId))
    return True
    
if __name__ == "__main__":
    main()

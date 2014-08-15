#!/usr/bin/python 

"""
    A simple scorer that reads the CMU Event Mention Detection Format 
    data and produce a mention based F-Scores

    This scorer needs will require token files as well to conduct evaluation
"""
import math
import errno
import argparse
import logging
import sys
import os
import heapq
from itertools import izip

commentMarker = "#"
bodMarker = "#BeginOfDocument" #mark begin of a document 
eodMarker = "#EndOfDocument" #mark end of a document

logger = logging.getLogger()

invisible_words = set(['the','a','an','I','you','he','she','we','they','his','her','my','your','mine','yours','our','ours','who','what','where','when'])

gf = None
sf = None
tokenDir = "."

diffOut = None

docScores = []

tokenJoiner = ","
tokenFileExt = ".tkn"

spanSeperator = ";"
spanJoiner = "_"

class EvalMethod:
    Token, Char = range(2)

def createParentDir(p):
    try:
        head,tail = os.path.split(p)
        if head != "":
            os.makedirs(head)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def main():
    global gf
    global sf
    global diffOut
    global tokenDir
    
    parser = argparse.ArgumentParser(description="Event mention scorer, which conducts token based scoring, your system and gold standard should follows the token-based format. The character based scoring is currently retained for comparison, which requires character based format.")
    parser.add_argument("-g","--gold",help="Golden Standard",required=True)
    parser.add_argument("-s","--system",help="System output",required=True)
    parser.add_argument("-d","--comparisonOutput",help="Compare and help show the difference between system and gold") 
    parser.add_argument("-o","--output",help="Optional evaluation result redirects")
    parser.add_argument("-c","--charMode",action='store_true',help="Option for character based scoring, the default one is token based")
    parser.set_defaults(charMode=False)
    parser.add_argument("-p","--tokenPath",help="Path to the directory containing the tokens, will use current directory if not specified, it will be required when token mode is activated to remove invisible words")
    args = parser.parse_args()
    
    stream_handler=None
    evalOut = None
    if args.output is not None:   
        outPath = args.output
        createParentDir(outPath)
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

    if args.comparisonOutput is not None:
        diffOutPath = args.comparisonOutput
    else:
        diffOutPath = "diff.tbf"
    
    createParentDir(diffOutPath)
    diffOut = open(diffOutPath,'w')

    if args.tokenPath is not None:
        if os.path.isdir(args.tokenPath):
            logger.error("Will search token files in "+args.tokenPath)
            tokenDir = args.tokenPath
        else:
            logger.error("Cannot find given token directory at " +args.tokenPath+", will try search for currrent directory")

    #token based eval mode
    evalMode = EvalMethod.Token
    
    if args.charMode:
        evalMode = EvalMethod.Char
        logger.debug("NOTE: Using character based evaluation")

    while True:
        res = evaluate(evalMode)
        if not res:
            break

    totalTp = 0
    totalFp = 0
    totalRealisCorrect = 0
    totalTypeCorrect = 0
    totalGoldMentions = 0
    totalPrec = 0
    totalRecall = 0
    totalRealisAccuracy = 0
    totalTypeAccuracy = 0
    validDocs = 0

    logger.info("========Document results==========")
    for (tp,fp,typeCorrect,realisCorrect,goldMentions,docId) in docScores:
        prec = tp/(tp+fp) if tp + fp > 0 else float('nan')
        recall = tp/goldMentions if goldMentions > 0 else float('nan')
        docF1 = 2 * prec * recall / (prec + recall) if prec + recall > 0 else float('nan')
        typeAccuracy = typeCorrect/goldMentions
        realisAccuracy = realisCorrect/goldMentions
        logger.info("TP\tFP\t#Gold\tPrec\tRecall\tF1\tType\tRealis\tDoc Id")
        logger.info("%.2f\t%.2f\t%d\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%s"%(tp,fp,goldMentions,prec,recall,docF1,typeAccuracy,realisAccuracy,docId))
        
        if math.isnan(prec) or math.isnan(recall):
            #no mentions annotated, treat as invalid file 
            pass
        else:
            validDocs += 1
            totalTp += tp
            totalFp += fp 
            totalGoldMentions += goldMentions
            totalPrec += prec 
            totalRecall += recall
            totalRealisAccuracy += realisAccuracy
            totalTypeAccuracy += typeAccuracy
            totalRealisCorrect += realisCorrect
            totalTypeCorrect += typeCorrect

    logger.info("\n=======Final Results=========")
    microPrec = totalTp/(totalTp+totalFp) if totalTp+ totalFp > 0 else float('nan')
    microRecall = totalTp/totalGoldMentions if totalGoldMentions > 0 else float('nan')
    microF1 = 2*microPrec*microRecall/(microPrec+microRecall) if microPrec+microRecall > 0 else float('nan')
    microTypeAccuracy = totalTypeCorrect / totalGoldMentions if totalGoldMentions > 0 else float('nan')
    microRealisAccuracy = totalRealisCorrect / totalGoldMentions if totalGoldMentions > 0 else float('nan')

    macroPrec = totalPrec/validDocs if validDocs > 0 else float('nan')
    macroRecall = totalRecall/validDocs if validDocs > 0 else float('nan')
    macroF1 = 2*macroPrec*macroRecall/(macroPrec+macroRecall) if macroPrec+macroRecall > 0 else float('nan')
    macroTypeAccuracy = totalTypeAccuracy / validDocs if validDocs > 0 else float('nan')
    macroRealisAccuracy = totalRealisAccuracy / validDocs if validDocs > 0 else float('nan')

    logger.info("Precision (Micro Average): %.4f",microPrec)
    logger.info("Recall (Micro Average):%.4f",microRecall)
    logger.info("F1 (Micro Average):%.4f",microF1)
    logger.info("Mention type detection accuracy (Micro Average):%.4f",microTypeAccuracy)
    logger.info("Mention realis status accuracy (Micro Average):%.4f",microRealisAccuracy)
    
    logger.info("Precision (Macro Average): %.4f", macroPrec)
    logger.info("Recall (Macro Average): %.4f", macroRecall)
    logger.info("F1 (Macro Average): %.4f", macroF1)
    logger.info("Mention type detection accuracy (Macro Average):%.4f",macroTypeAccuracy)
    logger.info("Mention realis status accuracy (Macro Average):%.4f",macroRealisAccuracy)

    if evalOut is not None:
        evalOut.close()
    diffOut.close()

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
   
def parseSpans(s):
    """
    Method to parse the character based span 
    """
    spanStrs = s.split(spanSeperator)
    spans = []
    for spanStrs in spanStrs:
        span = list(map(int,spanStrs.split(spanJoiner)))
        spans.append(span)
    return spans

def parseTokenIds(s,invisibleIds):
    """
    Method to parse the token ids (instead of a span)
    """
    tokenStrs = s.split(tokenJoiner)
    tokenIds = set()
    for tokenStr in tokenStrs:
        tokenId = int(tokenStr)
        if not tokenId in invisibleIds:
            tokenIds.add(tokenId)
        else:
            #logger.debug("Token Id %d is filtered"%(tokenId))
            pass
    
    return tokenIds

def parseCharBasedLine(l):
    '''
    Method to parse the character based line, which does not support
    removal of invisible words
    '''
    fields = l.split("\t")
    if (len(fields) != 8):
        logger.error("Output are not correctly formatted")
    spans = parseSpans(fields[3])
    mentionType = fields[5]
    realisStatus = fields[6]
    return (spans,mentionType,realisStatus)

def parseTokenBasedLine(l,invisibleIds):
    """
    parse the line, get the token ids, remove invisible ones
    """
    fields = l.split("\t")
    if (len(fields) != 8):
        logger.error("Output are not correctly formatted")
    tokenIds = parseTokenIds(fields[3],invisibleIds)
    mentionType = fields[5]
    realisStatus = fields[6]
    return (tokenIds,mentionType,realisStatus)

def parseLine(l,evalMode,invisibleIds):
    if evalMode == EvalMethod.Token:
        return parseTokenBasedLine(l,invisibleIds)
    else:
        return parseCharBasedLine(l)

def validateSpans(spans):
    lastEnd = -1
    for span in spans:
        if len(span) == 2 and span[1] > span[0]:
            pass
        else:
            logger.error(span+" is not a valid span")    
            sys.exit(1)
        if span[0] < lastEnd:
            logger.error("Spans cannot overlaps")
            sys.exit(1)

def spanOverlap(span1, span2):
    """
    return the number of characters that overlaps
    """
    if span1[1] > span2[0] and span1[0] < span2[1]:
        #find left end 
        leftEnd = span1[0] if span1[0] < span2[0] else span2[0]
        #find right end 
        rightEnd = span1[1] if span1[1] > span2[1] else span2[1]
        return rightEnd - leftEnd
    else:
        #no overlap 
        return 0

def computeCharOverlapScore(gSpans,sSpans):
    """
    character based overlap score
    """
    #validate system span 
    validateSpans(sSpans)

    gLength = 0
    for s in gSpans:
        gLength += (s[1]-s[0])

    sLength = 0
    for s in sSpans:
        sLength += (s[1]-s[0])
    
    totalOverlap = 0.0
    for gSpan in gSpans:
        for sSpan in sSpans:
            totalOverlap += spanOverlap(gSpan,sSpan)
 
    #choose to use the longer length
    deno = gLength if gLength < sLength else sLength

    return totalOverlap/deno

def computeTokenOverlapScore(gTokens,sTokens):
    """
    token based overlap score
    """
    
    totalOverlap = 0.0
    
    for sToken in sTokens:
        if sToken in gTokens:
            totalOverlap += 1

    gLength = len(gTokens)
    sLength = len(sTokens)

    if totalOverlap == 0:
        return 0

    #deno = gLength if gLength > sLength else sLength

    prec = totalOverlap / sLength
    recall = totalOverlap / gLength

    #return totalOverlap/deno
    return 2*prec*recall / (prec+recall)


def computeOverlapScore(systemOutputs,goldAnnos,evalMode): 
    if evalMode == EvalMethod.Token:
        return computeTokenOverlapScore(systemOutputs,goldAnnos)
    else:
        return computeCharOverlapScore(systemOutputs,goldAnnos)

def evaluate(evalMode):    
    (gLines,sLines,docId) = getNextDoc()
   
    if not gLines:
        return False

    invisibleIds = set() if evalMode == EvalMethod.Char else  getInvisibleWordIDs(docId)

    systemId = ""
    if len(sLines) > 0:
        fields = sLines[0].split("\t")
        if len(fields) > 0:
            systemId = fields[0]

    #parse the lines in file 
    systemMentionTable = []
    goldMentionTable = []

    for sl in sLines:
        systemOutputs,sytemMentionType,systemRealis = parseLine(sl,evalMode,invisibleIds)
        systemMentionTable.append(( systemOutputs,sytemMentionType,systemRealis ))

    for gl in gLines:
        goldAnnos,goldMentionType,goldRealis = parseLine(gl,evalMode,invisibleIds)
        goldMentionTable.append(( goldAnnos,goldMentionType,goldRealis ))
    
    #Store list of mappings with the score as a priority queue
    allGoldSystemMappingScores = []
    
    #first item in middle list store list of system mentions that mapped to it, second item is the overlap score 
    assignedGold2SystemMapping = [([],-1)]*len(gLines) 

    for systemIndex, (systemOutputs,sytemMentionType,systemRealis)in enumerate(systemMentionTable):
        largestOverlap = -1.0
        corresIndex = -1

        for index,  (goldAnnos,goldMentionType,goldRealis)  in enumerate(goldMentionTable):
            overlap = computeOverlapScore(goldAnnos,systemOutputs,evalMode)
            if len(goldAnnos) == 0:
                logger.debug("Found empty gold standard")
                logger.debug(gl)

            if (overlap > 0):
                #maintaining a max heap based on overlap score
                heapq.heappush(allGoldSystemMappingScores,(-overlap,systemIndex,index))

    mappedSystemMentions = set()
    numGoldFound = 0

    while len(allGoldSystemMappingScores) != 0:
        negMappingScore,mappingSystemIndex,mappingGoldIndex = heapq.heappop(allGoldSystemMappingScores)
        if not mappingSystemIndex in mappedSystemMentions:
                if  assignedGold2SystemMapping[mappingGoldIndex][1] == -1:
                    assignedGold2SystemMapping[mappingGoldIndex] = ([mappingSystemIndex],-negMappingScore)
                    numGoldFound += 1
                else:
                    assignedGold2SystemMapping[mappingGoldIndex][0].append(mappingSystemIndex)

                mappedSystemMentions.add(mappingSystemIndex)

    tp = 0.0
    fp = 0.0
    typeCorrect = 0.0
    realisCorrect = 0.0

    for goldIndex, (systemIndices, score) in enumerate(assignedGold2SystemMapping):
        if score > 0: # -1 indicates no mapping
            tp += score

            portionalScore = 1.0 / len(systemIndices)

            for systemIndex in systemIndices:
                if systemMentionTable[systemIndex][2] == goldMentionTable[goldIndex][2]:
                    realisCorrect += portionalScore

                if systemMentionTable[systemIndex][1] == goldMentionTable[goldIndex][1]:
                    typeCorrect += portionalScore


    diffOut.write(bodMarker+" "+docId+"\n")

    for gIndex, gLine in enumerate(gLines):
        goldContent = gLine.split("\t",1)
        systemIndex, mappingScore = assignedGold2SystemMapping[gIndex]
        scoreOut = "%.4f"%mappingScore if mappingScore != -1 else "-"
        diffOut.write("%s\t%s\t%s\n"%(systemId,goldContent[1],scoreOut))
    diffOut.write(eodMarker+" "+"\n")

    #unmapped system mentions are considered as false positive
    fp += len(sLines) - numGoldFound

    docScores.append((tp,fp,typeCorrect,realisCorrect,len(gLines),docId))
    return True
    
if __name__ == "__main__":
    main()

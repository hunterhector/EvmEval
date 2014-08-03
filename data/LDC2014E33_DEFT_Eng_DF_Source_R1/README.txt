          DEFT English Discussion Forum Source For Annotation R1 

                              LDC2014E33

                       Linguistic Data Consortium
                             April 18, 2014


1. Introduction

This package comprises source files that have been selected and processed for
the first increment DEFT English Discussion Forum Source For Annotation.  The
current package contains source data for continuous multi-post (CMP) units from
the English Discussion Forum selected for ERE annotation.  AMR and Committed
Belief annotation will make use of this same data set.  As annotation and data
selection are ongoing, we will plan to provide additional increments when new
batches of source data are added to the annotation pipeline.

2. Contents

./README.txt
  This file

./docs/filestats.tab
  File inventory, including post and word count as well as ERE status for each file.
  Status includes:
      1p-done: Completed first pass annotation on ERE
      1p-in-progress: currently in first annotation of ERE
      2p-done: Completed second pass annotation on ERE
      in-queue: Not yet annotated for ERE
      rejected: Reviewed and rejected for ERE annotation

  Note: Since ERE annotation is on-going, the status will change after this release. 
  Note: Files with "rejected" status may not be suitable for this round of ERE, 
        but may be suitable for ERE annotation in the future with new specifications.

./docs/cmp2df.tab
  Mapping info for each file to its original discussion forum thread

./data/source/discussion_forum
  These directories contain all of the source documents.  

3. Data Profile and Format

    Genre      Files   posts    Words
    ------------------------------------
    DF         1232    5949     963434
    ------------------------------------

4. Using the Data

All source documents are in the English Discussion Forum genre.  Due to the
length of many discussion forum threads, annotation of entire threads for
DEFT is impractical.  Therefore, LDC has selected units we call Continuous
Multi-Posts (CMPs), which consist of a continuous run of posts from a
thread.  The length of a CMP is between 100-1000 words.  In the case of a
short thread, this may indeed be the entire thread; in the case of longer
threads, the CMP is a truncated version of the thread (and it is possible
that there may be more than one CMP that comes from a single original
thread).  CMPs can be mapped back to the original full thread.  The
cmp2df.tab under ./docs/ lists where the CMPs are drawn from.  Note that
each CMP is an XML fragment rather than a full XML document, and so should
be treated as raw text (it is not expected to pass XML validation).

4.1 Offset Calculation

Because CMP is extracted verbatim from source XML files, its content
is escaped according to the XML specification.  The offsets of text extents
are based on this escaped text.  For example, in ERE annotation, the 
entity_mention, relation_mention, and event_mention XML elements all 
have attributes or contain sub-elements which use character offsets to 
identify text extents in the source.  The offset gives the start character 
of the text extent and the length attribute is added to the offset to find 
the string end character.  Offset counting starts from the initial 
character, character 0, of the source document and includes newlines.

5. Data selection

The source data pool comes from English discussion forum threads that 
have been manually reviewed and selected for BOLT annotation.  Automatic 
data selection was performed based on a set of event trigger words 
pulled from previous ACE and ERE annotation and manually edited in order 
to reduce the number of documents returned containing instances of 
trigger words of which the majority would not be instances of targeted
ERE event types.

Following the automatic filtering based on event trigger words, the
documents returned were ranked according to frequency of search hits. 
Documents included in the top tier of the ranking were then filtered for
redundancy.  An automatic duplication check was performed such that the
documents were ranked in terms of least redundancy, resulting in a
prioritization of documents to be annotated with little to no quoted
material.

Additionally, ERE annotators reviewed each assigned document prior to
performing exhaustive ERE annotation on that document.  If documents were
deemed to fall below a specified level of ERE richness, annotators
rejected the documents and did not perform ERE annotation on those
documents; filestats.tab under the docs/ directory indicated the status 
of each CMP in the ERE annotation pipeline. 

6. Contact Information

  Stephanie Strassel <strassel@ldc.upenn.edu>  PI
  Jonathan Wright    <jdwright@ldc.upenn.edu>  Technical oversight
  Haejoong Lee       <haejoong@ldc.upenn.edu>  Corpus Lead Developer
  Zhiyi Song         <zhiyi@ldc.upenn.edu>     DEFT collection manager

-------------------

README Update Log
  Created: Zhiyi Song, April 16, 2014
  Updated: David Graff, April 17, 2014


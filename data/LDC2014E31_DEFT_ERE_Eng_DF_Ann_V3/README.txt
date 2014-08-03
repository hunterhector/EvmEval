                  DEFT ERE English Discussion Forum Annotation V3

                              LDC2014E31

                       Linguistic Data Consortium
                             July 25, 2014
  

0.0 What is new in V3
  --188 source and annotation files are added
  
0.1 What's new in V2
  --85 source and annotation files are added
  --Additional QC were performed in annotation released in V1
  
1. Introduction

DARPA's Deep Exploration and Filtering of Text (DEFT) program aims to
address remaining capability gaps in state-of-the-art natural language
processing technologies related to inference, causal relationships and
anomaly detection.  In support of DEFT, LDC is providing source data
and core resources for system development.

Entity, Relation, and Event (ERE) annotation is a core resource
provided to train developing systems in detecting and coreferencing
the three namesake elements for the task. Annotators completing ERE
annotation primarily perform exhaustive tagging and coreference of
valid entities in a provided source document. Afterwards, valid
relations and events from the same document are annotated with
previously-tagged entities included as arguments. Lastly, annotators
perform coreference on all of the event mentions they have
annotated. Relation coreference is an automated process and is not
manually performed by annotators. For more information on ERE
annotations processes, please refer to the guidelines included in this
release.

This is the second cumulative release of ERE annotations for English 
Discussion Forum data in DEFT.

2. Contents

./README.txt
  This file
	
./docs/deft_ere.2.0.0.dtd
  DTD for ERE xml annotation files.	

./docs/cmp2df.tab
  Mapping info for each file to its original discussion forum thread

./docs/DEFT_Phase1_ERE_Annotation_Guidelines_Entities_V1.8.pdf
./docs/DEFT_Phase1_ERE_Annotation_Guidelines_Relations_V1.4.pdf
./docs/DEFT_Phase1_ERE_Annotation_Guidelines_Events_V1.6.pdf
  ERE annotation guidelines
	
./docs/ERE_Stats.tab
  Entity, Relation, and Event XML element counts for each file.

./data/source/discussion_forum
  These directories contain all of the source documents used for the
  annotations in this release.  
  
./data/ere/discussion_forum
  These directories contain all of the .xml annotation files.  

3. Data Profile and Format

Entity / Relation / Event annotation volumes

Genre      Files   Words  Entities (mentions)  Relations  Events
------------------------------------------------------------------
 DF        466    360,647  12,663  (49,425)    3,636      1,687
------------------------------------------------------------------

ERE annotation files have an ere.xml extension, and are in XML format.

For a full description of the elements, attributes, and structure of the ERE 
annotation files, please see the DTD in the docs directory of this release.

4. Using the Data

All ERE documents are in the English Discussion Forum genre. Since the 
source English Discussion Forum threads are very long, the threads are 
further split into continuous multi-post (CMP) unit for ERE annotation.  
The mpinfo.tab under ./docs/ lists where the CMPs are drawn from. Note
that CMP is an XML fragment rather than a full XML document.

4.1 Offset Calculation

All ERE XML files (file names "*.ere.xml") represent stand-off annotation of
source CMP files (file names "*.cmp.txt") and use offsets to refer to the text
extents. Because CMP is extracted verbatim from source XML files, its content
is escaped according to the XML specification.  The offsets of text extents
are based on this escaped text. The entity_mention, relation_mention, and
event_mention XML elements all have attributes or contain sub-elements which
use character offsets to identify text extents in the source.  The offset
gives the start character of the text extent and the length attribute is added
to the offset to find the string end character.  Offset counting starts from
the initial character, character 0, of the source document and includes
newlines.

4.2 Proper ingesting of XML

Character offsets and lengths for text extents are calculated based on "raw"
XML where XML meta-characters are escaped. For example, a reference to the
corporation "AT&T" will appear in CMP as "AT&amp;T". ERE annotation on this
string will cite a length of 8 characters (not 4). This string is stored in
the ERE XML file as "AT&amp;amp;T" because of XML escaping, but returns to
"AT&amp;T" when it is read using an XML parser.

5. ERE Annotation Pipeline

5.1 Data selection

Automatic data selection was performed based on a set of event trigger
words pulled from previous ACE and ERE annotation and manually edited
in order to reduce the number of documents returned containing instances
of trigger words of which the majority would not be instances of targeted
ERE event types.

Following the automatic filtering based on event trigger words, the
documents returned were ranked according to frequency of search hits. 
Documents included in the top tier of the ranking were then filtered for
redundancy. An automatic duplication check was performed such that the
documents were ranked in terms of least redundancy, resulting in a
prioritization of documents to be annotated with least amount of quoted
material.

Additionally, annotators reviewed each assigned document prior to
performing exhaustive ERE annotation on that document. If documents were
deemed to fall below a specified level of ERE richness, annotators
rejected the documents and did not perform ERE annotation on those
documents.

5.2 ERE Annotation

LDC annotators performed exhaustive ERE annotation on 278 continuous multi-
post documents. The data are annotated for all tasks by one annotator and then
second-pass annotated by a senior annotator or team leader. The first pass 
annotation is called 1P. The second pass annotation is called 2P. For 1P, 
a single junior annotator completes all tasks (entities, relations and events) 
for a file. For 2P, a more experienced senior annotator reviews the first-pass 
annotations and corrects any errors they identify. After 2P, additional corpus-
wide quality control (QC) spot-checks are conducted on 2P data by the team 
leader and selected senior annotators. Refer to section 5.3 for detailed QC
procedures.

The full annotation process for ERE annotation is represented below:

              1P: entities
                  relations
                  events
                  |
                  V
              2P: entities
                  relations
                  events
                  |
                  V
              QC: entities
                  relation
                  events
                  
Annotation consisted of tagging all mentions of a set of
targeted entities, relations and events, as well as marking coreference
for entities and events (coreference of relations is done automatically).
While annotation of a single document was performed individually,
annotators maintained many ongoing cooperative discussions regarding
difficult annotation issues and specific fringe examples. As this data
represents the first large-scale effort to perform ERE annotation on 
discussion forum data, annotators encountered a number of new phenomena
to which they had not previously encountered in Proxy and OSC data (two
genres similar to newswire in both content and form). Annotators worked
together to formulate consistent approaches to such phenomena that, while
novel in some cases, were consistent with pre-existing ERE guidelines.

Sometimes the CMPs contain quoted texts either from external source or from
the same CMP or thread. The quoted texts are annotated if they contain 
taggable entities, relations or events. 

5.3 Quality Control

After manual quality control on individual files, LDC also conducted 
corpus wide scan which includes:

    -- Manual scan of all PRO mentions for outliers 
    -- Manual scan of all NOM mentions with different entity type values 
       in different parts of the corpus 
    -- Manual scan of all NAM mentions with different entity type values 
       in different parts of the corpus 
    -- Search for relation arguments in violation of the Blocking Rule as
       defined in the annotation guidelines
    -- Manual scan of relation triggers to review trigger extents
    -- Manual scan of event triggers to review event type and subtype values
    -- Manual scan of event triggers that are also tagged as entity
    -- Manual scan of event triggers that are more than 3 words
    -- Manual scan of date arguments in event that are not normalized

All identified outliers are then manually reviewed and corrected if needed. 

These manual QC checks are done in parallel with automatic validation checks
of the data during extraction and preparation of annotation files for
delivery.

6. Data Validation

For all text extent references, it was verified that the combination of docid, 
offset, and length was a valid reference to a string identical to content of 
XML text extent element.

 - Verified trigger text extent references valid
 - Verified arg text extent references valid
 - Verified entity mention text extent references valid
 - Verified each ERE kits in delivery received annotations
 - Validated XML against DTD using xmllint (part of xmllib library)

Checks were also performed to identify and correct systematic errors that
occurred for certain event subtypes and argument types.

7. Known Issues

The 38 of the 466 *.cmp.txt files, and 16 of the 466 *.ere.xml files,
contain text strings with UTF-8 characters in the Unicode code-point
range U+0085 - U+0097.  These code points in Unicode are non-printing
"control characters" (they are taken into account in computing
character offsets, but are not visible).  Based on their distribution
in the text, these characters were originally single-byte non-ASCII
(non-Unicode) punctuation marks (apostrophe, quote, etc., presumably
from a CP1252-encoded source) that somehow were mis-handled during a
conversion to UTF-8 encoding.  Altogether, there are 185 of these
characters in the source data, and 36 in the annotation xml.

While the occurrences in the ere.xml files will exactly match the
corresponding regions of the source txt files to which the annotations
refer, these strings may fail to match equivalent strings elsewhere in
the data and annotations, due to the obscure code-point differences in
the intended/expected punctuation marks.


8. Contact Information

  Stephanie Strassel <strassel@ldc.upenn.edu>  PI
  Jonathan Wright    <jdwright@ldc.upenn.edu>  Technical oversight
  Haejoong Lee       <haejoong@ldc.upenn.edu>  Corpus Lead Developer
  Zhiyi Song         <zhiyi@ldc.upenn.edu>     ERE annotation project manager
  Tom Riese          <riese@ldc.upenn.edu>     ERE annotation lead annotator
-------------------

README Update Log
  Created: Zhiyi Song, April 14, 2014
  Updated: Jeremy Getman, April 15, 2014
  Updated: Zhiyi Song, April 15, 2014
  Updated: Zhiyi Song, May 14, 2014
  Updated: Zhiyi Song, July 25, 2014
  Updated: David Graff, July 28, 2014


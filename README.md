Event Mention Evaluation (EvmEval)
=========

This repository conducts pre-tokenization, file conversion, and scoring for event mention detection. It consists of the following three pieces of code:
 1. A token file factory based on the Stanford tokenizer
 2. A simple converter from Brat annotation tool format to CMU detection format
 3. A scorer that can score system performance based on CMU detection format

To use the software, we need to prepare the CMU format annotation file from the Brat annotation output using "brat2tokenFormat.py". The scorer can then take 2 documents in such format, one as gold standard data, one as system output. The scorer also need the token files produced by the tokenizer. The usage of these codes are described below. 

Use the example shell scripts "example_run.sh" to perform all the above steps in the sample documents 

brat2tokenFormat.py:
--------------------

Features
---------

1. ID convention

The default set up follows Brat v1.3 ID convention: 
  - T: text-bound annotation
  - R: relation
  - E: event
  - A: attribute
  - M: modification (alias for attribute, for backward compatibility)
  - N: normalization [new in v1.3]
  - #: note

Further development might allow customized ID convention.

2. This code only scan and detect event mentions and its attributes. Event arguments and entities are currently not handled. Annotations other than Event Mention (with its attributes and Text Spans) will be ignored, which means, it will only read "E" annotations and its related attributes.

3. Discontinuous text-bound annotations will be supported

Usage
-----

	brat2tokenFormat.py [-h] (-d DIR | -f FILE) -t TOKENPATH [-o OUT]
                           [-e EXT] [-i EID] [-w]

It accepts a single file name or a directory name that contains the Brat annotation output. 
The converter also requires token offset files that shares the same name with the annotation
file, with extension .tkn. The converter will search for the token file in the directory 
specified by '-t' argument

	Arguments:
	  -d DIR, --dir DIR     directory of the annotation files
	  -f FILE, --file FILE  name of one annotation file
	  -t TOKENPATH, --tokenPath TOKENPATH
							directory to search for the corresponding token files

	Optional Arguments:
	  -h, --help            show help message and exit
	  -o OUT, --out OUT     output path, 'converted' in the current path by default
	  -e EXT, --ext EXT     output extension, 'tbf' by default
	  -i EID, --eid EID     an engine id that will appears at each line of the
							output file. 'brat_conversion' will be used by default
	  -w, --overwrite       force overwrite existing output file
	  -s, --source          true if the annotations are done on source data,
	                           default is false
	  -b, --debug           turn debug mode on

scorer.py:
----------

Features
---------
Produce F1-like scoring by mapping system mentions to gold standard mentions,
read the scoring documentation for more details.

Usage
-----
	scorer.py [-h] -g GOLD -s SYSTEM -d COMPARISONOUTPUT [-o OUTPUT] -t
              TOKENPATH [-w]

Event mention scorer, which conducts token based scoring, system and gold
standard should follow the token-based format. The character based scoring is
currently retained for testing purpose, which requires character based format.

	Required arguments:
	  -g GOLD, --gold GOLD  Golden Standard
	  -s SYSTEM, --system SYSTEM
							System output
	  -d COMPARISONOUTPUT, --comparisonOutput COMPARISONOUTPUT
							Compare and help show the difference between system
							and gold
	  -t TOKENPATH, --tokenPath TOKENPATH
                        	Path to the directory containing the token mappings
                        	file 
	Optional arguments:  
	  -h, --help            show this help message and exit
	  -o OUTPUT, --output OUTPUT
							Optional evaluation result redirects
	  -w, --overwrite       force overwrite existing comparison file
	  -b, --debug           turn debug mode on

Event Mention Evaluation (EvmEval)
=========

This repository conducts pre-tokenization, file conversion, and scoring for event mention detection. It consists of the following three pieces of code:
 1. A token file factory based on the Stanford tokenizer
 2. A simple converter from Brat annotation tool format to CMU detection format
 3. A scorer that can score system performance based on CMU detection format

To use the software, we need to prepare the CMU format annotation file from the Brat annotation output using "brat2tokenFormat.py". The scorer can then take 2 documents in such format, one as gold standard data, one as system output. The scorer also need the token files produced by the tokenizer. The usage of these codes are described below. 

Use the example shell scripts "example_run.sh" to perform all the above steps in the sample documents, if success, you will find scoring results in the example_data directory 

Contents:
---------
├── LICENSE							Contains Licenses
│   ├── README
│   └── apache-v2.0
├── README.md						This file
├── brat2tokenFormat.py				The BRAT to evaluation format converter
├── example_data					Example data directory
│   ├── README.txt						Explain example data
│   ├── ann								Example annotations folder
│   │   └── example.tkn.ann1				One example annotation file
│   ├── sample_system_A.tbf				Example system output A
│   ├── sample_system_B.tbf				Example system output B
│   ├── tkn								Example token tables folder
│   │   └── example.txt.tab1				One example token table
│   └── txt								Example tokenized data
│       └── example.txt						One example tokenized file
├── example_run.sh					Shell script to perform a example run of both conversion and scoring
└── scorer.py						The scorer


Naming Convention:
-------------------
The following scripts need to find corresponding files by docid and file extension, so the file extension will be provided exactly. The script have default values for these extensions, but may require additional argument if extensions are changed.

Here is how to find the extension:

For tokenization table, they normally have the following name:

<docid>.txt.tab

In such case, the file extension is ".txt.tab", both the converter and scorer assume this as a default extension. If not, change them with "-te" argument

For brat annotation files, they normally have the following name:

<docid>.tkn.ann

In such case, the file extension is ".tkn.ann", the converter assume this as the default extention. If not, change it with "-ae" argument

The example_run.sh shell demostrate how to deal with extensions other than the default ones

Tokenization table files format:
--------------------------------
These are tab-delimited files which map the tokens to their tokenized files. A mapping table contains 3 columns for each row, and the rows contain an orderd listing of the
document's tokens. The columns are:
  token_id:   A string of "t" followed by a token-number beginning at 0
  token_str:  The literal string of a given-token
  tkn_begin:  Index of the token's first character in the tkn file
  tkn_end:    Index of the token's last character in the tkn file

Please note that all 4 fields are required and will be used:
	-- The converter will use token_id, tkn_begin, tkn_end to convert characters to token id
    -- The scorer will use the token_str to detect invisible words 

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
                           [-oe EXT] [-i EID] [-w] [-te TOKEN_TABLE_EXTENSION]
                           [-ae ANNOTATION_EXTENSION] [-b]

This converter converts Brat annotation files to one single token based event
mention description file (CMU format). It accepts a single file name or a
directory name that contains the Brat annotation output. The converter also
requires token offset files that shares the same name with the annotation
file, with extension .txt.tab. The converter will search for the token file in
the directory specified by '-t' argument

	Arguments:
	  -d DIR, --dir DIR     directory of the annotation files
	  -f FILE, --file FILE  name of one annotation file
	  -t TOKENPATH, --tokenPath TOKENPATH
                        directory to search for the corresponding token files

	Optional arguments:
	  -h, --help            show this help message and exit
	  -o OUT, --out OUT     output path, 'converted' in the current path by
							default
	  -oe EXT, --ext EXT    output extension, 'tbf' by default
	  -i EID, --eid EID     an engine id that will appears at each line of the
							output file. 'brat_conversion' will be used by default
	  -w, --overwrite       force overwrite existing output file
	  -te TOKEN_TABLE_EXTENSION, --token_table_extension TOKEN_TABLE_EXTENSION
							any extension appended after docid of token table
							files. Default is .txt.tab
	  -ae ANNOTATION_EXTENSION, --annotation_extension ANNOTATION_EXTENSION
							any extension appended after docid of annotation
							files. Default is .tkn.ann
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
                 TOKENPATH [-w] [-te TOKEN_TABLE_EXTENSION] [-b]

Event mention scorer, which conducts token based scoring, system and gold
standard files should follows the token-based format.

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
	  -te TOKEN_TABLE_EXTENSION, --token_table_extension TOKEN_TABLE_EXTENSION
							any extension appended after docid of token table
							files. Default is .txt.tab
	  -b, --debug           turn debug mode on

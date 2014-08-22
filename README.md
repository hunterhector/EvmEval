Event Mention Evaluation (EvmEval)
=========

This repostory conducts Event Mention Detection and Conversion
1. A simple converter from Brat annotation tool format to CMU detection format
2. A scorer that can score system performance based on CMU detection format

Example shell scripts can be found in the "run" directory

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
							output file
	  -w, --overwrite       force overwrite existing output file

scorer.py:
----------

Features
---------
Produce F1-like scoring by mapping system mentions to gold standard mentions,
read the scoring documentation for more details.

Usage
-----
	scorer.py [-h] -g GOLD -s SYSTEM -d COMPARISONOUTPUT [-o OUTPUT] [-c]
                 [-t TOKENPATH] [-w]

Event mention scorer, which conducts token based scoring, system and gold
standard should follows the token-based format. The character based scoring is
currently retained for testing purpose, which requires character based format.

	Required arguments:
	  -g GOLD, --gold GOLD  Golden Standard
	  -s SYSTEM, --system SYSTEM
							System output
	  -d COMPARISONOUTPUT, --comparisonOutput COMPARISONOUTPUT
							Compare and help show the difference between system
							and gold

	Optional arguments:  
	  -h, --help            show this help message and exit
	  -o OUTPUT, --output OUTPUT
							Optional evaluation result redirects
	  -c, --charMode        Option for character based scoring, the default one is
							token based, this argument is only retained for
							testing purposes
	  -t TOKENPATH, --tokenPath TOKENPATH
							Path to the directory containing the tokens, will use
							current directory if not specified, it will be
							required when token mode is activated to remove
							invisible words
	  -w, --overwrite       force overwrite existing comparison file

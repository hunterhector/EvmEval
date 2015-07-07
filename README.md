<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Event Mention Evaluation (EvmEval)](#event-mention-evaluation-evmeval)
  - [Naming Convention](#naming-convention)
  - [Tokenization table files format](#tokenization-table-files-format)
  - [scorer.py](#scorerpy)
    - [*Features*](#features)
    - [*Usage*](#usage)
  - [validator.py](#validatorpy)
    - [*Usage*](#usage-1)
  - [brat2tbf.py](#brat2tbfpy)
    - [*Features*](#features-1)
    - [*Usage*](#usage-2)
  - [LDC-XML-to-Brat converter](#ldc-xml-to-brat-converter)
    - [*Requirements of the software*](#requirements-of-the-software)
    - [*How to run the software*](#how-to-run-the-software)
    - [Assumptions of the software](#assumptions-of-the-software)
  - [Token File Maker](#token-file-maker)
    - [*Prerequisites*](#prerequisites)
    - [*Usage*](#usage-3)
  - [visualize.py](#visualizepy)
    - [*Text Base Visualization*](#text-base-visualization)
    - [*Web Base Visualization*](#web-base-visualization)
    - [*Usage*](#usage-4)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


Event Mention Evaluation (EvmEval)
=========

This repository conducts, file conversion, and scoring for event mention detection. It consists of the following three pieces of code:
 1. A simple converter from Brat annotation tool format to CMU detection format
 2. A scorer that can score system performance based on CMU detection format
 3. A visualizer that use Embedded Brat Viewer

To use the software, we need to prepare the CMU format annotation file from the Brat annotation output using "brat2tbf.py". The scorer can then take 2 documents in such format, one as gold standard data, one as system output. The scorer also need the token files produced by the tokenizer. The usage of these codes are described below. 

Use the example shell scripts "example_run.sh" to perform all the above steps in the sample documents, if success, you will find scoring results in the example_data directory 


Naming Convention
-------------------
The following scripts need to find corresponding files by docid and file extension, so the file extension will be provided exactly. The script have default values for these extensions, but may require additional argument if extensions are changed.

Here is how to find the extension:

For tokenization table, they normally have the following name:

    <docid>.tab

In such case, the file extension is ".tab", both the converter and scorer assume this as a default extension. If not, change them with "-te" argument.

For brat annotation files, they normally have the following name:

    <docid>.ann

In such case, the file extension is ".ann", the converter assume this as the default extention. If not, change it with "-ae" argument

Tokenization table files format
--------------------------------
These are tab-delimited files which map the tokens to their tokenized files. A mapping table contains 3 columns for each row, and the rows contain an orderd listing of the
document's tokens. The columns are:
  - token_id:   A string of "t" followed by a token-number beginning at 0
  - token_str:  The literal string of a given-token
  - tkn_begin:  Index of the token's first character in the tkn file
  - tkn_end:    Index of the token's last character in the tkn file

Please note that all 4 fields are required and will be used:
  - The converter will use token_id, tkn_begin, tkn_end to convert characters to token id
  - The scorer will use the token_str to detect invisible words 
  
The tokenization table files are created using our [automatic tool](#token-file-maker), which wraps the Stanford tokenizer and provide boundary checks.

scorer.py
----------
The current scorer can score event mention detection and coreference based on the (.tbf) format. It also require the token table files to detect invisible words and to generate
CoNLL style coreference files.

### *Features*
1. Produce F1-like scoring by mapping system mentions to gold standard mentions,
read the scoring documentation for more details.
2. Be able to produce a comparison output indicating system and gold standard differences:
  a. A text based comparison output (-d option)
  b. A web based comparison output using Brat's embedded visualization (-v option)
3. If specified, it will generate temporary conll format files, and use the conll reference-scorer to produce coreference scores

### *Usage*
	usage: scorer_v1.3.py [-h] -g GOLD -s SYSTEM [-d COMPARISON_OUTPUT]
                          [-o OUTPUT] [-c COREF] -t TOKEN_PATH [-of OFFSET_FIELD]
                          [-te TOKEN_TABLE_EXTENSION] [-b]

	
Event mention scorer, which conducts token based scoring, system and gold standard files should follows the token-based format.

    Required Arguments:
      -g GOLD, --gold GOLD  Golden Standard
      -s SYSTEM, --system SYSTEM
                            System output
      -t TOKEN_PATH, --token_path TOKEN_PATH
                            Path to the directory containing the token mappings
                            file   
    Optional Arguments:
      -h, --help            show this help message and exit                                                    
      -d COMPARISON_OUTPUT, --comparison_output COMPARISON_OUTPUT
                            Compare and help show the difference between system
                            and gold
      -o OUTPUT, --output OUTPUT
                            Optional evaluation result redirects, put eval result
                            to file
      -c COREF, --coref COREF
                            Eval Coreference result output, need to put the
                            referenceconll coref scorer in the same folder with
                            this scorer
      -of OFFSET_FIELD, --offset_field OFFSET_FIELD
                            A pair of integer indicates which column we should
                            read the offset in the token mapping file, index
                            startsat 0, default value will be [2, 3]
      -te TOKEN_TABLE_EXTENSION, --token_table_extension TOKEN_TABLE_EXTENSION
                            any extension appended after docid of token table
                            files. Default is [.txt.tab]
      -b, --debug           turn debug mode on

validator.py
--------------------
The validator check whether the supplied "tbf" file follows assumed structure . 

### *Usage*
    validator.py [-h] -s SYSTEM -t TOKEN_PATH [-of OFFSET_FIELD]
                        [-te TOKEN_TABLE_EXTENSION] [-b]
    
    Event mention scorer, which conducts token based scoring, system and gold
    standard files should follows the token-based format.
    
    optional arguments:
      -h, --help            show this help message and exit
      -s SYSTEM, --system SYSTEM
                            System output
      -t TOKEN_PATH, --token_path TOKEN_PATH
                            Path to the directory containing the token mappings
                            file
      -of OFFSET_FIELD, --offset_field OFFSET_FIELD
                            A pair of integer indicates which column we should
                            read the offset in the token mapping file, index
                            startsat 0, default value will be [2, 3]
      -te TOKEN_TABLE_EXTENSION, --token_table_extension TOKEN_TABLE_EXTENSION
                            any extension appended after docid of token table
                            files. Default is [.txt.tab]
      -b, --debug           turn debug mode on

brat2tbf.py
--------------------
This is a tool that converts Brat Annotation format to TBF format. We currently try to make as little assumption as possible. However, in order to resolve
coreference transitive redirect automatically, the relation name for coreference must be named as "Coreference". We also develop for event coreference only.

### *Features*

1. ID convention

The default set up follows Brat v1.3 ID convention: 
  - T: text-bound annotation
  - R: relation
  - E: event
  - A: attribute
  - M: modification (alias for attribute, for backward compatibility)
  - N: normalization [new in v1.3 of Brat]
  - #: note

Further development might allow customized ID convention.

2. This code only scan and detect event mentions and its attributes. Event arguments and entities are currently not handled. Annotations other than Event Mention (with its attributes and Text Spans) will be ignored, which means, it will only read "E" annotations and its related attributes.

3. Discontinuous text-bound annotations will be supported

### *Usage*

	brat2tokenFormat.py [-h] (-d DIR | -f FILE) -t TOKENPATH [-o OUT]
                           [-oe EXT] [-i EID] [-w] [-te TOKEN_TABLE_EXTENSION]
                           [-ae ANNOTATION_EXTENSION] [-b]

This converter converts Brat annotation files to one single token based event mention description file (CMU format). It accepts a single file name or a directory name that contains the Brat annotation output. The converter also requires token offset files that shares the same name with the annotation file, with extension .txt.tab. The converter will search for the token file in	the directory specified by '-t' argument

	Required Arguments:
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
 
LDC-XML-to-Brat converter
------------
This software converts LDC's XML format for the [TAC KBP 2015 Event Nugget task](http://cairo.lti.cs.cmu.edu/kbp/2015/event/) to the [Brat format](http://brat.nlplab.org/standoff.html).  More specifically, it converts LDC's event nuggets and coreferences to events and coreference links that can be viewed via the Brat web interface.  Brat annotation configurations for output are available at directory `src/main/resources/`.
The software is located at the direcotry: ldc-xml-to-brat-converter, you can built it from source using Maven.  You can also find a pre-compiled version in the bin/g directory

### *Requirements of the converter*
The software requires Java 1.8. A precompiled jar locates at bin directory. To compile the project from source you will also need Maven 2.7+.

### *How to run it*
```
$ java LdcXmlToBratConverter
Option           Description     
------           -----------     
-h               help            
-i <input dir>   input directory 
-o <output dir>  output directory
```

### Assumptions of the software
The software assumes that the following two types of input files are given with the fixed file extensions.
- text file (with tags): *.mpdf.xml
- annotation file: *.rich_ere.xml
 
 
Token File Maker
------------
### *Requirements of the file maker*
The software requires Java 1.8. A precompiled jar locates at bin directory. To compile the project from source you will also need Maven 2.7+.

### *Prerequisites*
Our tokenizer implementation is based on the tokenizer in the Stanford CoreNLP tool .  The software is implemented in Java, and its requirements are as follows:
 1.	Java 1.8
 2.	The same number of text files and brat annotation files (*.ann) with the same file base name

### *Usage*

    java -jar bin/token-file-maker-1.0.3-jar-with-dependencies.jar -a <annotation> -e <extension> [-h] -o <output> [-s <separator>] -t <text>
        -a <annotation>   annotation directory
        -e <extension>    text file extension
        -h                print this message
        -o <output>       output directory
        -s <separator>    separator chars for tokenization
        -t <text>         text directory

 
visualize.py
------------

The visualization is provided as a mechanism to compare different output, which is optional and can be ignored if one is only interested in the scores. This code maybe update frequently. Please refer to the command line "-h" for detailed instructions.

The visualize code represent mention differences in JSON, which is then passed to [Embedded Brat](http://brat.nlplab.org/embed.html) .  

Recent changes make visualizing clusters possible by creating additional JSON object. When enabled, there will be a cluster selector on the webpage, one could select the cluster and all other event mentions will hide.

### *Text Base Visualization*
The text based Visualization can be generated using the "scorer.py", by supplying the "-d"
argument. The format is straightforward, a text document is produced for comparison.
The annotation of both systems are displayed in one line, separated by "|"

### *Web Base Visualization*
The web base visualization takes the text visualization file, then: 
  1. convert them to Brat Embedded JSON format and store it at the visualization 
  folder (visualization/json)
  2. It will start a server at the visualization folder using localhost:8000
  3. Now user can browse the locally hosted site for comparison
  4. User can stop the server when done, and restart it at anytime using "start.sh", it is 
  no longer necessary to regenerate the JSON data if one only wish to use the old ones
  

### *Usage*
    usage: visualize.py [-h] -d COMPARISON_OUTPUT -t TOKENPATH [-x TEXT]
                    [-v VISUALIZATION_HTML_PATH] [-of OFFSET_FIELD]
                    [-te TOKEN_TABLE_EXTENSION] [-se SOURCE_FILE_EXTENSION]

Mention visualizer, will create a side-by-side embedded visualization from the
mapping

    Required Arguments:
      -d COMPARISON_OUTPUT, --comparison_output COMPARISON_OUTPUT
                            The comparison output file between system and gold,
                            used to recover the mapping
      -t TOKENPATH, --tokenPath TOKENPATH
                            Path to the directory containing the token mappings
                            file
    Optional Arguments:
      -h, --help            show this help message and exit                    
      -x TEXT, --text TEXT  Path to the directory containing the original text
      -v VISUALIZATION_HTML_PATH, --visualization_html_path VISUALIZATION_HTML_PATH
                            The Path to find visualization web pages, default path
                            is [visualization]
      -of OFFSET_FIELD, --offset_field OFFSET_FIELD
                            A pair of integer indicates which column we should
                            read the offset in the token mapping file, index
                            startsat 0, default value will be [2, 3]
      -te TOKEN_TABLE_EXTENSION, --token_table_extension TOKEN_TABLE_EXTENSION
                            any extension appended after docid of token table
                            files. Default is [.txt.tab]
      -se SOURCE_FILE_EXTENSION, --source_file_extension SOURCE_FILE_EXTENSION
                            any extension appended after docid of source
                            files.Default is [.tkn.txt]

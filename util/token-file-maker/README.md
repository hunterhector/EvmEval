<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Token File Maker](#token-file-maker)
  - [*Prerequisites*](#prerequisites)
  - [*Usage*](#usage)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

Token File Maker
----------------
We use a standard tokenization so that participants can submit results in terms of the tokens. However, we decided to move to a simpler character based evaluation so that we can easily extend our support to multiple languages.

### *Prerequisites*
Our tokenizer implementation is based on the tokenizer in the Stanford CoreNLP tool .  The software is implemented in Java, and its requirements are as follows:
 1.	Java 1.8
 2.	The same number of text files and brat annotation files (*.ann) with the same file base name

### *Usage*
```
usage: java -jar bin/token-file-maker-1.0.4-jar-with-dependencies.jar -a <annotation> -e <extension> [-h] -o
       <output> [-s <separator>] -t <text>
 -a <annotation>   annotation directory
 -e <extension>    text file extension
 -h                print this message
 -o <output>       output directory
 -s <separator>    separator chars for tokenization
 -t <text>         text directory
```

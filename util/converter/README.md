<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Converters](#converters)
- [Requirements of the software](#requirements-of-the-software)
- [Running use pre-packaged jar files](#running-use-pre-packaged-jar-files)
  - [How to run the Rich ERE to Brat converter (rich_ere_to_brat_converter.jar)](#how-to-run-the-rich-ere-to-brat-converter-rich_ere_to_brat_converterjar)
  - [How to run the Rich ERE to TBF converter (rich_ere_to_tbf_converter.jar)](#how-to-run-the-rich-ere-to-tbf-converter-rich_ere_to_tbf_converterjar)
  - [Note](#note)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Converters
This package contains two converters, a Rich ERE to Brat format and a Rich ERE to TBF format converter.

The Rich ERE to Brat converter converts LDC's Rich ERE XML format annotated for the [TAC KBP 2015 Event Nugget task](http://cairo.lti.cs.cmu.edu/kbp/2015/event/) to the [Brat format](http://brat.nlplab.org/standoff.html).  More specifically, it converts LDC's event nuggets and coreferences to events and coreference links that can be viewed via the Brat web interface.  Brat annotation configurations for output are available at directory `src/main/resources/`.

The Rich ERE to TBF converter converts Rich ERE format to the [event nugget evaluation format](http://cairo.lti.cs.cmu.edu/kbp/2016/event/Event-Mention-Detection-scoring-2016-v28).

## Requirements of the software
The software requires Java 1.7 or higher.

## Running use pre-packaged jar files
We've created two self-contained JAR files in the bin/ directory under project root.

### How to run the Rich ERE to Brat converter (rich_ere_to_brat_converter.jar)
You can see its usage with the following command:
```
$ java -jar target/converter-1.0.3-jar-with-dependencies.jar -h
Option                            Description              
------                            -----------              
-a <annotation dir>               annotation directory       
--ae <annotation file extension>  annotation file extension  
-d                                whether to detag text      
-h                                help                       
-i <input mode>                   input mode ("event-nugget")
-o <output dir>                   output directory           
-t <text dir>                     text directory             
--te <text file extension>        text file extension        
```

### How to run the Rich ERE to TBF converter (rich_ere_to_tbf_converter.jar)
You can see its usage with the following command:
```
java -jar bin/rich_ere_to_tbf_converter.jar -h  
Option                            Description                
------                            -----------                
-a <annotation dir>               annotation directory       
--ae <annotation file extension>  annotation file extension  
-h                                help                       
-i <input mode>                   input mode ("event-nugget")
-o <output file>                  output file                
-t <text dir>                     text directory             
--te <text file extension>        text file extension        
```

### Note
For both converters, please be aware of the file paths and extensions. The converter will not be able to find the resources with incorrect path. The file extensions should be specified correctly so that the system can match the source text and ere annotations.
An example command:

```
java -jar bin/rich_ere_to_tbf_converter.jar -a ../data/project_data/LDC/LDC2015E105_DEFT_Rich_ERE_Chinese_Training_Annotation/data/ere  --ae rich_ere.xml -t ../data/project_data/LDC/LDC2015E105_DEFT_Rich_ERE_Chinese_Training_Annotation/data/source  --te cmp.txt -o LDC2015E105.tbf
```
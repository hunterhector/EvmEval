# LDC XML to Brat converter
This software converts LDC's XML format for the [TAC KBP 2015 Event Nugget task](http://cairo.lti.cs.cmu.edu/kbp/2015/event/) to the [Brat format](http://brat.nlplab.org/standoff.html).

# How to run the software
You can see its usage with the following command:
$ java LdcXmlToBratConverter
Option           Description     
------           -----------     
-h               help            
-i <input dir>   input directory 
-o <output dir>  output directory

# Assumptions of the software
The software assumes that the following two types of input files are given with the fixed file extensions.
- text file (with tags): *.mpdf.xml
- annotation file: *.rich_ere.xml


#!/usr/bin/env bash

#change this line to the LDC annotation data folder
ldc_text_dir=data/private/LDC2015E73/data/source
ldc_ann_dir=data/private/LDC2015E73/data/event_nugget

#change the following lines to your desired output folder
brat_output_dir=data/private/conversion_test/ann
token_table_dir=data/private/conversion_test/tkn
output_tbf_basename=data/private/conversion_test/gold

echo "Running XML to Brat Converter..."
java -jar bin/converter-1.0.2-jar-with-dependencies.jar -t "$ldc_text_dir" -te "txt" -a "$ldc_ann_dir" -ae "event_nuggets.xml" -o "$brat_output_dir"
echo "Running tokenizer..."
java -jar bin/token-file-maker-1.0.4-jar-with-dependencies.jar -a "$brat_output_dir" -t "$brat_output_dir" -e txt -o "$token_table_dir"
echo "Converting to TBF format"
python ./brat2tbf.py -t "$token_table_dir" -d "$brat_output_dir" -o "$output_tbf_basename" -w

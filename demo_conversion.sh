#!/usr/bin/env bash
# This file demonstrate how to run the end-to-end conversion procedures. There are two possible type of annotated data:
# 1. Event Nugget only
# 2. Nugget and hopper
# 3. This file shows both conversion, user might just pick one of them for their specific use case.

#change these lines to the LDC annotation data folder
ldc_text_dir=data/private/LDC2015E73_TAC_KBP_2015_Event_Nugget_Training_Data_Annotation_V2/data/source
ldc_nugget_dir=data/private/LDC2015E73_TAC_KBP_2015_Event_Nugget_Training_Data_Annotation_V2/data/event_nugget
ldc_hopper_dir=data/private/LDC2015E73_TAC_KBP_2015_Event_Nugget_Training_Data_Annotation_V2/data/event_hopper

#change the following lines to your desired output folder
brat_output_dir=data/private/conversion_test_v2/ann
token_table_dir=data/private/conversion_test_v2/tkn
nugget_output_tbf_filename=gold_nugget
nugget_output_tbf_basename=data/private/conversion_test_v2/$nugget_output_tbf_filename
hopper_output_tbf_filename=gold_hopper
hopper_output_tbf_basename=data/private/conversion_test_v2/$hopper_output_tbf_filename

# The following are for nugget conversion.
echo "Running XML to Brat Converter for nuggets..."
java -jar bin/converter-1.0.3-jar-with-dependencies.jar -t "$ldc_text_dir" -te "txt" -a "$ldc_nugget_dir" -ae "event_nuggets.xml" -o "$brat_output_dir" -i event-nugget
echo "Running tokenizer..."
java -jar bin/token-file-maker-1.0.4-jar-with-dependencies.jar -a "$brat_output_dir" -t "$brat_output_dir" -e "txt" -o "$token_table_dir"
echo "Converting to TBF format"
python bin/brat2tbf.py -t "$token_table_dir" -d "$brat_output_dir" -o "$nugget_output_tbf_basename" -w
echo "Validating converted files."
python ./validator.py -t "$token_table_dir" -s "$nugget_output_tbf_basename"".tbf"
echo "Validation done, see log at : "$nugget_output_tbf_filename".tbf.errlog"

# The following are for hopper conversion.
echo "Running XML to Brat Converter for hoppers..."
java -jar bin/converter-1.0.3-jar-with-dependencies.jar -t "$ldc_text_dir" -te "txt" -a "$ldc_hopper_dir" -ae "event_hoppers.xml" -o "$brat_output_dir"
echo "Running tokenizer..."
java -jar bin/token-file-maker-1.0.4-jar-with-dependencies.jar -a "$brat_output_dir" -t "$brat_output_dir" -e "txt" -o "$token_table_dir"
echo "Converting to TBF format"
python bin/brat2tbf.py -t "$token_table_dir" -d "$brat_output_dir" -o "$hopper_output_tbf_basename" -w
echo "Validating converted files."
python bin/validator.py -t "$token_table_dir" -s "$hopper_output_tbf_basename"".tbf"
echo "Validation done, see log at : "$hopper_output_tbf_filename".tbf.errlog"


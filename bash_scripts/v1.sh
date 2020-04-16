#!/usr/bin/env bash

export config=../input/config_files/v0.json
export input=../output/dfn_objects/
export output=../output/dfn_objects/polysemy_profiles

mkdir -p $output/polysemy_profiles

cd ../lib
python categorize_lemma_to_lemma_polysemy.py \
 --config_path=$config \
 --input_folder=$input \
 --output_folder=$output \
 --rbn_pos="noun" \
 --fn_pos="N" \
 --verbose=1 > $output/noun.out 2> $output/noun.err 

 python categorize_lemma_to_lemma_polysemy.py \
 --config_path=$config \
 --input_folder=$input \
 --output_folder=$output \
 --rbn_pos="verb" \
 --fn_pos="V" \
 --verbose=1 > $output/verb.out 2> $output/verb.err 

python categorize_lemma_to_lemma_polysemy.py \
 --config_path=$config \
 --input_folder=$input \
 --output_folder=$output \
 --rbn_pos="adjective" \
 --fn_pos="A" \
 --verbose=1 > $output/adjective.out 2> $output/adjective.err 

python add_relation_rbn_to_fn_lu.py --config_path=$config --input_folder=$input --use_wn_polysemy="True" --pos="adjective-noun-verb" --verbose=1 > $output/v1.out 2> $output/v1.err


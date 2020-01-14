#!/usr/bin/env bash

cd ..

python combine_resources.py --config_path="config_files/v0.json" --output_folder="output" --use_cache="True" --verbose=4

#python categorize_lemma_to_lemma_polysemy.py --config_path="config_files/v0.json" --input_folder="output" --output_folder="polysemy_profiles" --rbn_pos="noun" --fn_pos="N" --verbose=1
#python categorize_lemma_to_lemma_polysemy.py --config_path="config_files/v0.json" --input_folder="output" --output_folder="polysemy_profiles" --rbn_pos="adjective" --fn_pos="A" --verbose=1
#python categorize_lemma_to_lemma_polysemy.py --config_path="config_files/v0.json" --input_folder="output" --output_folder="polysemy_profiles" --rbn_pos="verb" --fn_pos="V" --verbose=1

#python add_relation_rbn_to_fn_lu.py --config_path="config_files/v0.json" --input_folder="output" --use_wn_polysemy="True" --pos="adjective" --verbose=1


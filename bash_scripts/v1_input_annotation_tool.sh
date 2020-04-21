#!/usr/bin/env bash


cd ../lib

python input_annotation_tool.py --config_path="../input/config_files/v1.json"

cd ../output/annotation/iteration_1
zip -r tool_input.zip tool_input


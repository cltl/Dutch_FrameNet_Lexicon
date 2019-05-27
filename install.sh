#!/usr/bin/env bash

rm -rf resources
mkdir resources

cd resources
git clone https://github.com/cltl/FrameNet_annotations_on_SoNaR
cd FrameNet_annotations_on_SoNaR
pip install -r requirements.txt
cd scripts
python main.py --annotator=A1 --output_folder='bins'
python main.py --annotator=A2 --output_folder='bins'
cd ..
cd ..

mkdir wiktionary
cd wiktionary
wget https://zenodo.org/record/1286991/files/enwiktionary_translations.tar.gz
tar -xvzf enwiktionary_translations.tar.gz
cd ..

git clone https://github.com/cltl/FN_Reader
cd FN_Reader
pip install -r requirements.txt
bash install.sh
cd ..


git clone https://github.com/cltl/ODWN_Reader
cd ODWN_Reader
bash install.sh
pip install -r requirements.txt
python main.py --orbn_path="resources/orbn_1.0.xml" --odwn_path="resources/odwn_orbn_gwg-LMF_1.3.xml" --output_folder="output" --allowed_prefixes="r+c" --exclude_sub_NUMBER="True" --namespace="http://premon.fbk.eu/resource/" --short_namespace="pm"
python convert_mapping_to_json.py --path_to_excel="mapping_to_fn/Mapping.xlsx" --json_output_path="mapping_to_fn/mapping.json"
cd ..







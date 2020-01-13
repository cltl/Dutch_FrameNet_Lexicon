#!/usr/bin/env bash

rm -rf resources
mkdir resources

cd resources
mkdir premon
cd premon
wget https://knowledgestore.fbk.eu/files/premon/dataset/latest/premon-2018a-fn17-noinf.tql.gz
gunzip premon-2018a-fn17-noinf.tql.gz
cd ../..
python -c 'import rdf_utils;g = rdf_utils.load_nquads_file(path_to_nquad_file="resources/premon/premon-2018a-fn17-noinf.tql");rdf_utils.convert_nquads_to_nt(g, output_path="resources/premon/premon-2018a-fn17-noinf.nt")'

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

git clone https://github.com/cltl/run_open-sesame
cd run_open-sesame
pip install -r requirements.txt
bash install.sh
cd ..

git clone https://github.com/cltl/ODWN_Reader
cd ODWN_Reader
bash install.sh
pip install -r requirements.txt
python main.py --orbn_path="resources/orbn_n-v-a.xml" --odwn_path="resources/odwn_orbn_gwg-LMF_1.3.xml" --output_folder="output" --allowed_prefixes="r+c" --exclude_sub_NUMBER="True" --namespace="http://premon.fbk.eu/resource/" --short_namespace="pm"
python convert_mapping_to_json.py --path_to_excel="mapping_to_fn/Mapping.xlsx" --json_output_path="mapping_to_fn/mapping.json"
cd ..

git clone https://github.com/cltl/DutchSemCor_Reader
cd DutchSemCor_Reader
python load_dutchsemcor.py --input_folder="resources/1.2.1.HUMAN_ANNOTATIONS/" --output_folder="output" --prefixes="r" --verbose="1"



pip install nltk
python -c 'import nltk;nltk.download("wordnet")'







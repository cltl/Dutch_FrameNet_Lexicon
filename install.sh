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





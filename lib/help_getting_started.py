# general note
# I've put the imports needed for each resource in that part for clarity in how to load them.
import json
config_path = '../input/config_files/v0.json'
configuration = json.load(open(config_path))
verbose=1

# 1. How to load FrameNet object
# please download this file: http://kyoto.let.vu.nl/~postma/dfn/lexicon/combined_v1.p
# and store it somewhere on your computer
# the path where you stored is should be entered below:
import os
import pickle
import load_utils

load_utils.load_python_module(module_path='../resources/ODWN_Reader',
                              module_name='odwn_classes', verbose=0)

fn_object_path = '../output/dfn_objects/combined_v1.p'
assert os.path.exists(fn_object_path), f'{fn_object_path} does not exist. Please inspect'

with open(fn_object_path, 'rb') as infile:
    fn_obj = pickle.load(infile)

for frame_label, frame_obj in fn_obj.framelabel2frame_obj.items():
    to_break = False
    for lu_id, lu_obj in frame_obj.lu_id2lu_obj.items():
        if lu_obj.rbn_senses:
            print()
            print(frame_label)
            print(lu_obj)
            for rbn_dict in lu_obj.rbn_senses:
                print()
                print(rbn_dict)
                rbn_obj = rbn_dict['rbn_obj']
                print(rbn_obj.lemma)
                print(rbn_obj.sense_id)
            to_break = True

    if to_break:
        break

# 2. Wiktionary
from wiktionary_utils import load_wiktionary
# uncomment to load (takes a few minutes)
#nl2en, en2nl = load_wiktionary(configuration, verbose=verbose)

# 3. Load RBN
rbn_senseid2le_obj = pickle.load(open(configuration['path_rbn_objs'], 'rb'))

# 4. Load English WordNet
# TODO: we have to discuss the mapping of English WordNet part-of-speech to FN part-of-speech
from nltk.corpus import wordnet as wn

"""
Categorize mapping between Dutch and English into polysemy profiles

Usage:
  categorize_lemma_to_lemma_polysemy.py --config_path=<config_path> --input_folder=<input_folder> --output_folder=<output_folder> --rbn_pos=<rbn_pos> --fn_pos=<fn_pos> --verbose=<verbose>

Options:
    --config_path=<config_path>
    --input_folder=<input_folder> input folder with output from combine_resources.py (graph.p and combined.p)
    --rbn_pos=<rbn_pos> noun verb adjective adverb other
    --fn_pos=<fn_pos> supported: N V A Adv
    --output_folder=<output_folder>
    --verbose=<verbose> 0 --> no stdout 1 --> general stdout 2 --> detailed stdout

Example:
    python categorize_lemma_to_lemma_polysemy.py --config_path="config_files/v0.json" --input_folder="output" --output_folder="polysemy_profiles" --rbn_pos="verb" --fn_pos="V" --verbose=1
"""
from collections import defaultdict
import sys
import pickle
import os
import json
import pathlib
from docopt import docopt
from datetime import datetime

import networkx as nx
import graph_utils

from resources.ODWN_Reader import odwn_classes
# make sure pickled objects can be read into memory
sys.modules['odwn_classes'] = odwn_classes
from resources.ODWN_Reader import utils


def polysemy_profiles_to_category(polysemy_nl, polysemy_en):
    """
    """

    if polysemy_nl == 1:

        if polysemy_en == 1:
            category = 'm2m'
        elif polysemy_en >= 2:
            category = 'm2p'

    elif polysemy_nl >= 2:
        if polysemy_en == 1:
            category = 'p2m'
        elif polysemy_en >= 2:
            category = 'p2p'

    return category


assert polysemy_profiles_to_category(1, 1) == 'm2m'
assert polysemy_profiles_to_category(1, 2) == 'm2p'
assert polysemy_profiles_to_category(2, 1) == 'p2m'
assert polysemy_profiles_to_category(2, 2) == 'p2p'



# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

config_path = arguments['--config_path']
assert os.path.exists(config_path), f'{config_path} does not exist'
configuration = json.load(open(config_path))
verbose = int(arguments['--verbose'])

out_dir = pathlib.Path(arguments['--output_folder'])
if not out_dir.exists():
    out_dir.mkdir(parents=True)

# load objects
rbn_objs = pickle.load(open(configuration["path_rbn_objs"], 'rb'))
fn_obj = pickle.load(open(f"{arguments['--input_folder']}/combined.p", "rb"))
g = nx.read_gpickle(f"{arguments['--input_folder']}/graph.p")

# load polysemy info
lemma_pos2frame_objs = defaultdict(list)
for frame_label, frame_obj in fn_obj.frame_label2frame_obj.items():
    for lu_id, lu_obj in frame_obj.lu_id2lu_obj.items():
        lemma_pos2frame_objs[(lu_obj.lexeme,
                              lu_obj.pos)].append(frame_obj)


pol_info_df, \
pol_df, \
lemma_pos2le_ids = utils.load_polysemy_info(rbn_objs,
                                            pos={arguments['--rbn_pos']})

# query for paths
print('starting querying for paths', datetime.now())
all_paths = graph_utils.get_paths_from_rbn_to_fn(g,
                                                 from_prefix=f'(Dutch)',
                                                 to_prefix=f'LU-',
                                                 from_suffix=f'.{arguments["--fn_pos"]}',
                                                 maximum_length_path=1,
                                                 verbose=verbose)
print('ended querying for paths', datetime.now())

maximum_path_length = 2
statistics = defaultdict(set)

for path in all_paths:
    node_nl, node_en = path

    lemma_nl = g.node[node_nl]['attr']['lemma']
    pos_nl = g.node[node_nl]['attr']['pos']
    pol_nl = len(lemma_pos2le_ids[(lemma_nl, pos_nl)])

    lemma_en = g.node[node_en]['attr']['lemma']
    pos_en = g.node[node_en]['attr']['pos']
    pol_en = len(lemma_pos2frame_objs[(lemma_en, pos_en)])

    assert pos_nl == pos_en

    polysemy_cat = polysemy_profiles_to_category(pol_nl,
                                                 pol_en)

    value = ((lemma_nl, pos_nl), (lemma_en, pos_en))
    key = polysemy_cat

    statistics[key].add(value)

# save to file
output_path = out_dir / f'{arguments["--fn_pos"]}.p'
with open(output_path, 'wb') as outfile:
    pickle.dump(statistics, outfile)

if verbose:
    print(f'saved output to {output_path}')
    print(datetime.now())


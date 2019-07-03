"""
Exploit translation relation between monosemous Dutch and English lemmas

Usage:
  add_relation_rbn_to_fn_lu.py --config_path=<config_path> --input_folder=<input_folder> --use_wn_polysemy=<use_wn_polysemy> --pos=<pos> --verbose=<verbose>

Options:
    --config_path=<config_path>
    --input_folder=<input_folder> should contain combined.p and graph.p
    --use_wn_polysemy=<use_wn_polysemy> if 'True', we only include English lemma,pos combinations that are monosemous in WordNet
    --pos=<pos> RBN pos to use, e.g., 'noun-verb-adjective'
    --verbose=<verbose> 0 --> no stdout 1 --> general stdout 2 --> detailed stdout

Example:
    python add_relation_rbn_to_fn_lu.py --config_path="config_files/v0.json" --input_folder="output" --use_wn_polysemy="True" --pos="noun-verb-adjective" --verbose=1
"""
import json
import os
import pickle
import sys
from docopt import docopt
from collections import defaultdict
import networkx as nx
from nltk.corpus import wordnet as wn

from dfn_classes import fn_pos2wn_pos
from resources.ODWN_Reader import odwn_classes
# make sure pickled objects can be read into memory
sys.modules['odwn_classes'] = odwn_classes
from resources.ODWN_Reader import utils

# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()



config_path = arguments['--config_path']
rbn_pos = set(arguments['--pos'].split('-'))
fn_pos = {pos[0].upper()
          for pos in rbn_pos}
use_wn_filter = arguments['--use_wn_polysemy'] == 'True'
verbose = int(arguments['--verbose'])

assert os.path.exists(config_path), f'{config_path} does not exist'
configuration = json.load(open(config_path))

rbn_senseid2le_obj = pickle.load(open(configuration['path_rbn_objs'], 'rb'))
synset_id2synset_obj = pickle.load(open(configuration['path_synset_objs'], 'rb'))

pol_info_df, \
pol_df, \
lemma_pos2le_ids = utils.load_polysemy_info(rbn_senseid2le_obj,
                                            pos=rbn_pos)

frame_objs_path = os.path.join(arguments['--input_folder'], 'combined.p')
updated_frame_objs_path = os.path.join(arguments['--input_folder'], 'combined_v1.p')
graph_path = os.path.join(arguments['--input_folder'], 'graph.p')
updated_graph_path = os.path.join(arguments['--input_folder'], 'graph_v1.p')

for path in [frame_objs_path, graph_path]:
    assert os.path.exists(path), f'path {path} does not exist'

frame_label2frame_obj = pickle.load(open(frame_objs_path, 'rb'))

lemma_and_pos_en2lemma_pos_nl = defaultdict(set)
for pos in fn_pos:
    polysemy_profiles = pickle.load(open(f'polysemy_profiles/{pos}.p', 'rb'))
    for (lemma_nl, pos_nl), (lemma_en, pos_en) in polysemy_profiles['m2m']:
        lemma_and_pos_en2lemma_pos_nl[(lemma_en, pos_en)].add((lemma_nl, pos_nl))

# for every frame
for frame_label, frame_obj in frame_label2frame_obj.items():

    # for every lemma obj
    for lemma_obj in frame_obj.lemma_objs:

        # make sure it comes from Wiktionary and the lemma is Dutch
        if all([lemma_obj.provenance == 'wiktionary',
                lemma_obj.language == 'Dutch']):

            # retrieve the FrameNet LU object
            lu_obj = frame_obj.lu_id2lu_obj[lemma_obj.lu_id]
            if not hasattr(lu_obj, 'rbn_objs'):
                lu_obj.rbn_objs = set()

            key = (lu_obj.lexeme, lu_obj.pos)

            # here we will add the RBN ids to will be linked to this FrameNet Lexical Unit
            to_add = set()

            # if the english lemma and pos are part of the chosen polysemy profile
            if key in lemma_and_pos_en2lemma_pos_nl:
                dutch_lemma_pos = lemma_and_pos_en2lemma_pos_nl[key]

                if use_wn_filter:
                    wn_pos = fn_pos2wn_pos(lu_obj.pos)
                    assert wn_pos != 'UNMAPPABLE', f'could not map {lu_obj.pos} to WordNet'
                    synsets = wn.synsets(lu_obj.lexeme, wn_pos)
                    if len(synsets) >= 2:
                        if verbose >= 2:
                            print(f'skipping {lu_obj.lexeme} {lu_obj.pos} because wn polysemy of {len(synsets)}')
                        continue

                # if the dutch lemma and pos are part of the chosen polysemy profile
                if (lemma_obj.lemma, lemma_obj.pos) in dutch_lemma_pos:

                    # what are possible RBN senses?
                    sense_ids = lemma_pos2le_ids[(lemma_obj.lemma, lemma_obj.pos)]

                    # add synonyms?
                    for sense_id in sense_ids:

                        rbn_obj = rbn_senseid2le_obj[sense_id]
                        lu_obj.rbn_objs.add(rbn_obj.short_rdf_uri)

                        rbn_obj = rbn_senseid2le_obj[sense_id]
                        if rbn_obj.synset_id:
                            synset_obj = synset_id2synset_obj[rbn_obj.synset_id]
                            synonyms = {le_obj.short_rdf_uri
                                        for le_obj in synset_obj.synonyms
                                        if all(['cdb2.2_Manual' in le_obj.provenance_set,
                                                le_obj.sense_id != sense_id])
                                        }

                            for synonym in synonyms:
                                lu_obj.rbn_objs.add(synonym)

# determine the one to one relationships
sense_id2lu_ids = defaultdict(set)
lu_id2sense_ids = defaultdict(set)
for frame_label, frame_obj in frame_label2frame_obj.items():
    for lu_id, lu_obj in frame_obj.lu_id2lu_obj.items():
        if hasattr(lu_obj, 'rbn_objs'):
            if lu_obj.rbn_objs:
                for sense_id in lu_obj.rbn_objs:
                    sense_id2lu_ids[sense_id].add(lu_id)
                    lu_id2sense_ids[lu_id].add(sense_id)


# update graph
g = nx.read_gpickle(graph_path)
old_num_edges = len(g.edges())
added = 0
for frame_label, frame_obj in frame_label2frame_obj.items():
    for lu_id, lu_obj in frame_obj.lu_id2lu_obj.items():

        lu_obj.rbn2fn = set()

        for sense_id in lu_id2sense_ids[lu_id]:
            if len(sense_id2lu_ids[sense_id]) == 1:
                g.add_edge(lu_id, sense_id)
                lu_obj.rbn2fn.add(sense_id)
                if verbose >= 2:
                    print(lu_id, sense_id)
                added += 1

new_num_edges = len(g.edges())
assert (old_num_edges + added) == new_num_edges
if verbose:
    print(f'number of new edges: {added}')

print(f'written to {updated_graph_path}')
nx.write_gpickle(g, updated_graph_path)

# save to file
with open(updated_frame_objs_path, 'wb') as outfile:
    pickle.dump(frame_label2frame_obj, outfile)
    print(f'written to {updated_frame_objs_path}')


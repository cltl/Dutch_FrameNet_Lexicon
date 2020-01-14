"""
Combine information from Dutch resources that allow us to link ot English FrameNet

Usage:
  combine_resources.py --config_path=<config_path> --output_folder=<output_folder> --use_cache=<use_cache> --verbose=<verbose>

Options:
    --config_path=<config_path>
    --output_folder=<output_folder>
    --verbose=<verbose> 0 --> no stdout 1 --> general stdout 2 --> detailed stdout
    --use_cache=<use_cache>

Example:
    python combine_resources.py --config_path="config_files/v0.json" --output_folder="output" --use_cache="True" --verbose=1
"""
import json
import os
import sys
import pickle
import pathlib
from docopt import docopt
from datetime import datetime

import dfn_classes
import graph_utils

from sonar_utils import load_sonar_annotations
from wiktionary_utils import load_wiktionary
from resources.FN_Reader.stats_utils import load_framenet
import rbn_utils
import rdf_utils
from resources.ODWN_Reader import odwn_classes
# make sure pickled objects can be read into memory
sys.modules['odwn_classes'] = odwn_classes

import networkx as nx

# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

config_path = arguments['--config_path']
assert os.path.exists(config_path), f'{config_path} does not exist'
configuration = json.load(open(config_path))

out_dir = pathlib.Path(arguments['--output_folder'])
if not out_dir.exists():
    out_dir.mkdir(parents=True)

cache_dir = pathlib.Path(configuration['cache_folder'])
if not cache_dir.exists():
    cache_dir.mkdir(parents=True)
cache_path_translations = cache_dir / 'translations.p'

verbose=int(arguments['--verbose'])
rbn_filter = configuration['rbn_filter'] == 'True'
exclude_lemmas_with_spaces = configuration['exclude_lemmas_with_space'] == 'True'
use_cache = arguments['--use_cache'] == 'True'

if verbose >= 1:
    print('START TIME', datetime.now())

# load framenet
fn = load_framenet(version=configuration['fn_version'])

# load premon nt file
premon_nt = rdf_utils.load_nt_graph(nt_path=configuration['path_premon_nt'])

# load sonar annotations
frame2lexeme_objs_from_sonar, \
frame2lemma_objs_from_sonar, \
sonar_stats = load_sonar_annotations(configuration, verbose=verbose)


if all([use_cache,
        not cache_path_translations.exists()]):
    if verbose >= 1:
        print('extracting wikitionary translations from file (no cache used')
    nl2en, en2nl = load_wiktionary(configuration, verbose=verbose)
    with open(str(cache_path_translations), 'wb') as outfile:
        pickle.dump((nl2en, en2nl), outfile)
else:
    if verbose >= 1:
        print('loading wiktionary translations from cache')
    with open(str(cache_path_translations), 'rb') as infile:
        nl2en, en2nl = pickle.load(infile)

# load rbn information
mapping = json.load(open(configuration['mapping_rbn_featureset2fn_frames']))
rbn_senseid2le_obj = pickle.load(open(configuration['path_rbn_objs'], 'rb'))
rbn_objs = rbn_senseid2le_obj.values()
frame2rbn_objs, \
frame2feature_set_values= rbn_utils.load_frame2rbn_objs_via_subsumes_relation(fn,
                                                                              mapping,
                                                                              rbn_objs)

synset_id2synset_obj = pickle.load(open(configuration['path_synset_objs'], 'rb'))

# loop over framenet
fn_obj = dfn_classes.FrameNet()

for frame in fn.frames():

    frame_label = frame.name
    frame_def = frame.definition

    frame_obj = dfn_classes.Frame(fn_frame_obj=frame,
                                  frame_label=frame_label,
                                  definition=frame_def,
                                  fn_version=configuration['fn_version'],
                                  fn_url=frame.URL,
                                  rdf_prefix=configuration['rdf_prefix'],
                                  premon_nt=premon_nt)

    frame_obj.add_lu_objs(frame, frame_obj.rdf_prefix_uri)

    if verbose >= 4:
        continue

    # add lexeme information from sonar annotations
    if frame_label in frame2lexeme_objs_from_sonar:
        lexeme_objs = frame2lexeme_objs_from_sonar[frame_label]
        frame_obj.lexeme_objs = lexeme_objs

    # add lemme information from sonar annotations
    if frame_label in frame2lemma_objs_from_sonar:
        lemma_objs = frame2lemma_objs_from_sonar[frame_label]
        frame_obj.lemma_objs.extend(lemma_objs)

    # add lemma translations
    for lu_id, lu_obj in frame_obj.lu_id2lu_obj.items():
        translations = en2nl[lu_obj.lexeme]
        for translation in translations:
            lemma_obj = dfn_classes.Lemma(lemma=translation,
                                          frame_label=frame_obj.rdf_prefix_uri,
                                          provenance='wiktionary',
                                          language='Dutch',
                                          pos=lu_obj.pos,
                                          lu_id=lu_id)
            frame_obj.lemma_objs.append(lemma_obj)

    # add information from RBN
    if frame_label in frame2feature_set_values:
        frame_obj.rbn_feature_set_values.extend(frame2feature_set_values[frame_label])

    # perform filtering based on RBN information
    if rbn_filter:
        frame_obj.lemma_objs = dfn_classes.filter_based_on_rbn(frame_obj.lemma_objs,
                                                               rbn_objs,
                                                               verbose=verbose)

    # performing filtering based on whether there are spaces in the lemmas
    if exclude_lemmas_with_spaces:
        frame_obj.lemma_objs = dfn_classes.filter_based_on_spaces_in_lemma(frame_obj.lemma_objs,
                                                                           verbose=verbose)

    # make sure all Dutch lemma_pos ids have an identifier
    for lemma_obj in frame_obj.lemma_objs:
        if lemma_obj.language == 'Dutch':
            fn_obj.update_lemma_obj_with_lemmapos_id(lemma_obj)

    fn_obj.framelabel2frame_obj[frame_label] = frame_obj

# validate
fn_obj.validate_lemmapos_identifiers()

if verbose:
    print(fn_obj)

# load graph
g = graph_utils.load_graph(fn_obj.framelabel2frame_obj,
                           synset_id2synset_obj,
                           rbn_objs,
                           configuration['graph_options'],
                           verbose=verbose)

# save to file
output_path = out_dir / 'combined.p'
with open(output_path, 'wb') as outfile:
    pickle.dump(fn_obj, outfile)

graph_path = out_dir / 'graph.p'
nx.write_gpickle(g, graph_path)


if verbose:
    print(f'saved output to {output_path}')
    print(f'saved graph to {graph_path}')
    print(datetime.now())

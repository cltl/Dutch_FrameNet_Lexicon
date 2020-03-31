"""
Combine information from Dutch resources that allow us to link ot English FrameNet

Usage:
  create_dot_vizualizations.py --graph_path=<graph_path> --rbn_path=<rbn_path> --output_folder=<output_folder> --verbose=<verbose>

Options:
    --graph_path=<graph_path>
    --rbn_path=<rbn_path>
    --output_folder=<output_folder>
    --verbose=<verbose> 0 --> no stdout 1 --> general stdout 2 --> detailed stdout

Example:
    python create_dot_vizualizations.py --graph_path="output/graph_v1.p" --rbn_path="resources/ODWN_Reader/output/orbn.p" --output_folder="dot" --verbose="1"
"""
import pickle
from pathlib import Path
import graph_utils
import networkx as nx
from docopt import docopt
from datetime import datetime

import load_utils
odwn_classes = load_utils.load_python_module(module_path='../resources/ODWN_Reader',
                                           module_name='odwn_classes',
                                           verbose=1)

# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

g = nx.read_gpickle(arguments['--graph_path'])
senseid2rbn_obj = pickle.load(open(arguments['--rbn_path'], 'rb'))
rbn_objs = senseid2rbn_obj.values()
verbose = int(arguments['--verbose'])
out_dir = Path(arguments['--output_folder'])
if not out_dir.exists():
    out_dir.mkdir(parents=True)

lemma_pos = {(rbn_obj.lemma, rbn_obj.simple_pos)
             for rbn_obj in rbn_objs
             if rbn_obj.simple_pos in {'n'}}
if verbose:
    print('parts of speech: n')
    print(f'number of lemma and pos: {len(lemma_pos)}')

verbose=0
maximum_path_length=3
for index, (lemma, pos) in enumerate(lemma_pos):

    if index % 100 == 0:
        print(index, datetime.now())

    from_prefix = f'(pm)RBN-{lemma}-{pos}'
    to_prefix = f'(pm)fn1.7'

    all_paths = graph_utils.get_paths_from_rbn_to_fn(g,
                                                     from_prefix=from_prefix,
                                                     to_prefix=to_prefix,
                                                     maximum_length_path=maximum_path_length,
                                                     verbose=verbose)

    if all_paths:
        lemma_g = graph_utils.subgraph_in_dot(g,
                                              paths=all_paths,
                                              output_path=f'{str(out_dir)}/{lemma}-{pos}.gv')
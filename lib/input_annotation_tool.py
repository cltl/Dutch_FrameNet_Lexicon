"""
Create the input material for annotation of Dutch FrameNet
(performed by this tool: https://github.com/cltl/DutchFrameNetAnnotation)

Usage:
  input_annotation_tool.py --config_path=<config_path>

Options:
    --config_path=<config_path> JSON with settings for an Iteration

Example:
    python input_annotation_tool.py \
    --graph_path="../input/config_files/v1.json"\
"""
from docopt import docopt
import json
import os

from evaluation import create_annotation_folder

# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

settings = json.load(open(arguments['--config_path']))

tool_input = os.path.join(settings['iteration_annotation_folder'],
                          'tool_input')

create_annotation_folder(output_folder=tool_input,
                         graph_path=settings['graph_path'],
                         path_rbn_to_lu=settings['evaluation_set_path'],
                         overwrite=True,
                         verbose=1)

print(f'stored annotation input at {tool_input}')

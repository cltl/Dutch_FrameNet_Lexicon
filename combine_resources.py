"""
Combine information from Dutch resources that allow us to link ot English FrameNet

Usage:
  combine_resources.py --config_path=<config_path> --output_folder=<output_folder> --verbose=<verbose>

Options:
    --verbose=<verbose> 0 --> no stdout 1 --> general stdout 2 --> detailed stdout

Example:
    python combine_resources.py --config_path="config_files/v0.json" --output_folder="output" --verbose=1
"""
import json
import os
import pickle
import pathlib
from docopt import docopt

import dfn_classes

from sonar_utils import load_sonar_annotations
from wiktionary_utils import load_wiktionary
from resources.FN_Reader.stats_utils import load_framenet

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
    out_dir.mkdir(parents=True, exist_ok=True)

verbose=int(arguments['--verbose'])


# load sonar annotations
frame2lexeme_objs_from_sonar, sonar_stats = load_sonar_annotations(configuration, verbose=verbose)

nl2en, en2nl = load_wiktionary(configuration, verbose=verbose)

# loop over framenet
fn = load_framenet()
frame_label2frame_obj = dict()


for frame in fn.frames():

    frame_label = frame.name

    frame_obj = dfn_classes.EnFrame(frame_label=frame_label)

    # add information from sonar annotations
    if frame_label in frame2lexeme_objs_from_sonar:
        lexeme_objs = frame2lexeme_objs_from_sonar[frame_label]
        frame_obj.lexeme_objs = lexeme_objs

    for lemma_pos, lu_info in frame.lexUnit.items():
        lu_id = lu_info.ID

        for lemma_pos, lu in frame.lexUnit.items():
            lexeme_parts = [lexeme_part['name']
                            for lexeme_part in lu.lexemes]
            lexeme = ' '.join(lexeme_parts)

            translations = en2nl[lexeme]
            for translation in translations:
                lemma_obj = dfn_classes.Lemma(lemma=translation,
                                              frame_label=frame_label,
                                              provenance='wiktionary',
                                              lu_id=lu_id)
                frame_obj.lemma_objs.append(lemma_obj)

    frame_label2frame_obj[frame_label] = frame_obj


# save to file
output_path = out_dir / 'combined.p'
with open(output_path, 'wb') as outfile:
    pickle.dump(frame_label2frame_obj, outfile)

if verbose:
    print(f'saved output to {output_path}')

"""
Given a dfn_classes.FrameNet, this Python module loops over
the LUs of all frames. Provided, that there are links to the Referentie Bestand Nederlands
stored in the "rbn_senses" attribute of LUs, this module will convert them to the
format needed to include them in the NLTK format of FrameNet

Usage:
  convert_dfn_object_to_fn_format.py\
   --config_path=<config_path>\
   --verbose=<verbose>

Options:
    --config_path=<config_path> path to the configuration file, see ../input/config_files/to_fn_nltk.json for an exmaple
    --verbose=<verbose>

Example:
    python convert_dfn_object_to_fn_format.py --config_path="../input/config_files/to_fn_nltk.json" --verbose="2"
"""
import pickle
import json
from docopt import docopt

import load_utils
import rbn_utils

arguments = arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)

# load configuration
settings = json.load(open(arguments['--config_path']))
verbose = int(arguments['--verbose'])

# load orbn
load_utils.load_python_module(module_path='../resources/ODWN_Reader',
                              module_name='odwn_classes',
                              verbose=0)
sense_id_to_sense_obj = pickle.load(open(settings['paths']['orbn_path'],
                                         'rb'))

# load dfn_classes.FrameNet object
fn_obj = pickle.load(open(settings['paths']['fn_obj_path'], 'rb'))


rbnid_to_anno_type_to_luid_to_options = rbn_utils.load_rbn_sense_to_lu(fn_obj=fn_obj,
                                                                       settings=settings,
                                                                       verbose=verbose)


lu_json = {'lus' : [],
           'lus_to_annotate' : []}

for rbn_sense_id, anno_type_to_luid_to_options in rbnid_to_anno_type_to_luid_to_options.items():
    lu_id, rbn_dict, reason = rbn_utils.lu_decider(lu_options=anno_type_to_luid_to_options)

    if lu_id is not None:
        rbn_sense_id = rbn_dict['rbn_obj'].sense_id
        rbn_obj = sense_id_to_sense_obj[rbn_sense_id]

        annotation_category = rbn_dict['annotation_info']['annotation_category']
        rbn_matching_rel = settings['fn_nltk']['annotation_categories'][annotation_category]

        optional_lu_attrs = dict()
        if rbn_matching_rel:
            optional_lu_attrs['RBN_LU_ID'] = rbn_sense_id
            optional_lu_attrs['RBN_matching_relation'] = rbn_matching_rel
            optional_lu_attrs['FN_EN_LU_ID'] = lu_id[3:]
            optional_lu_attrs['Method'] = rbn_dict['provenance']

        fn_nltk_format,\
        attributes_to_annotate = rbn_obj.get_fn_nltk_format(frame=rbn_dict['frame'],
                                                            provenance=rbn_dict['annotation_info']['annotation_provenance'],
                                                            status="Created",
                                                            incorporated_fe=None,
                                                            timestamp=None,
                                                            optional_lu_attrs=optional_lu_attrs)
        if not attributes_to_annotate:
            lu_json['lus'].append(fn_nltk_format)
        else:
            lu_json['lus_to_annotate'].append(fn_nltk_format)

print()
print(f'RBN senses to be added: {len(lu_json["lus"])}')
print(f'RBN senses to be annotated: {len(lu_json["lus_to_annotate"])}')

with open(settings['fn_nltk']['lus_json'], 'w') as outfile:
    json.dump(lu_json,
              outfile,
              indent=4,
              sort_keys=True)

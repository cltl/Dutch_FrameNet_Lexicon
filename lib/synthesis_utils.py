import json
config_path = '../input/config_files/v0.json'
configuration = json.load(open(config_path))

from wiktionary_utils import load_wiktionary

# How to load FrameNet object
# please download this file: http://kyoto.let.vu.nl/~postma/dfn/lexicon/combined_v1.p
# and store it somewhere on your computer
# the path where you stored it should be entered below:
import os
import pickle
import load_utils

load_utils.load_python_module(module_path='../resources/ODWN_Reader',
                              module_name='odwn_classes', verbose=0)

fn_object_path = '../output/dfn_objects/combined_v1.p'
assert os.path.exists(fn_object_path), f'{fn_object_path} does not exist. Please inspect'

with open(fn_object_path, 'rb') as infile:
    fn_obj = pickle.load(infile)


def preprocess_framenet(verbose=0):
    """
    Extract information from FrameNet
    for the computation of descriptive statistics.

    :rtype: tuple
    :return:    (fn_form2fn_lu_ids,         dict for FN form -> FN LU id(s)
                pos_set,                    set for encountered POS in FN
                frame_label_pos2fn_lu_ids)  dict for (frame, None) -> FN LU id(s)
    """

    frames_absent_lus = set()

    pos_set = set()
    fn_form2fn_lu_ids = dict()
    frame_label_pos2fn_lu_ids = dict()
    for frame_label, frame_obj in fn_obj.framelabel2frame_obj.items():

        # frames without LUs (non-lexical LUs), these are ignored in the preprocessing, i.e. skipped in the next for-loop
        if not frame_obj.lu_id2lu_obj.items():
            frames_absent_lus.add(frame_label)

        for lu_id, lu_obj in frame_obj.lu_id2lu_obj.items():

            # update (form, POS) -> FN LU id(s) dictionary
            pos_set.add(lu_obj.pos)
            form_pos = (lu_obj.lexeme, lu_obj.pos)
            if form_pos not in fn_form2fn_lu_ids.keys():
                fn_form2fn_lu_ids[form_pos] = set()
            fn_form2fn_lu_ids[form_pos].add(lu_id)

            # update (frame, None) -> FN LU id(s) dictionary
            frame_label_pos = (frame_label, None)  # POS is not an attribute of a frame
            if frame_label_pos not in frame_label_pos2fn_lu_ids.keys():
                frame_label_pos2fn_lu_ids[frame_label_pos] = set()
            frame_label_pos2fn_lu_ids[frame_label_pos].add(lu_id)

    if verbose:
        n_frames_total = len(fn_obj.framelabel2frame_obj)
        n_frames_absent_lus = len(frames_absent_lus)
        n_frames_present_lu = len(fn_obj.framelabel2frame_obj) - len(frames_absent_lus)
        print(frames_absent_lus)
        print('\nThe FrameNet frames above are absent LUs...')
        print(f'FrameNet contains {n_frames_total} frames, '
              f'{n_frames_present_lu} possess at least 1 LU, '
              f'meaning {n_frames_absent_lus} are absent LU\n')

    return fn_form2fn_lu_ids, pos_set, frame_label_pos2fn_lu_ids


def wiki_direction(wiktionary_dict):
    """
    Extract information from Wiktionary in one direction
    for the computation of descriptive statistics.

    :rtype: dict
    :return: lemma_pos2translations for (form, None) -> translations
    """
    lemma_pos2translations = dict()
    for lemma, translations in wiktionary_dict.items():
        lemma_pos = (lemma, None) # no POS info present in Wiktionary, translation is form to form
        lemma_pos2translations[lemma_pos] = translations

    return lemma_pos2translations

def preprocess_wiki():
    """
    Extract information from Wiktionary in both directions
    for the computation of descriptive statistics.

    :rtype: tuple
    :return:    (nl_pos2en,     dict for (Dutch form, None) -> English form(s)
                en_pos2nl)      dict for (English form, None) -> Dutch form(s)
    """
    nl2en, en2nl = load_wiktionary(configuration)
    nl_pos2en = wiki_direction(nl2en)
    en_pos2nl = wiki_direction(en2nl)

    return nl_pos2en, en_pos2nl


def preprocess_rbn():
    """
    Extract information from RBN
    for the computation of descriptive statistics.

    :rtype: tuple
    :return:    (rbn_form2rbn_senseids,     dict for RBN form -> RBN LU id(s)
                pos_set)                    set for encountered POS in RBN
    """
    rbn_senseid2le_obj = pickle.load(open(configuration['path_rbn_objs'], 'rb'))

    pos_set = set()
    rbn_form2rbn_senseids = dict()
    for rbn_senseid, le_obj in rbn_senseid2le_obj.items():
        pos_set.add(le_obj.fn_pos)
        form_pos = (le_obj.lemma, le_obj.fn_pos)
        if form_pos not in rbn_form2rbn_senseids.keys():
            rbn_form2rbn_senseids[form_pos] = set()
        rbn_form2rbn_senseids[form_pos].add(rbn_senseid)

    return rbn_form2rbn_senseids, pos_set
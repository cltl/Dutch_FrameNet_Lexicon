import sys
import os
import pickle
from dfn_classes import Lexeme
from collections import defaultdict
from resources.FrameNet_annotations_on_SoNaR.scripts import sonar_classes
# make sure pickled objects can read into memory
sys.modules['sonar_classes'] = sonar_classes


def load_sonar_annotations(configuration, verbose=0):
    """
    load sonar annotations to
    frame_label -> list of Lexeme objects

    :param dict configuration: configuration (see config_files folder)

    :rtype: tuple
    :return: (mapping of frame_label -> lexeme objects,
              stats)
    """
    # load annotator information
    assert os.path.exists((configuration['path_sonar_annotator_1']))
    with open(configuration['path_sonar_annotator_1'], 'rb') as infile:
        annotator_1 = pickle.load(infile)

    assert os.path.exists((configuration['path_sonar_annotator_2']))
    with open(configuration['path_sonar_annotator_2'], 'rb') as infile:
        annotator_2 = pickle.load(infile)


    shared_keys = set(annotator_1) | set(annotator_2)
    merging_stats = {
        '# of shared_annotations' : len(shared_keys),
        '# of same frame annotations' : 0
    }

    provenance_label = 'sonar_fn_annotations'
    frame_label2lexeme_obj = defaultdict(list)

    for key in shared_keys:

        info_annotator_1 = annotator_1[key]
        info_annotator_2 = annotator_2[key]


        # check that both have only one frame annotated + it is the same one
        if all([len(info_annotator_1.frame) == 1,
                len(info_annotator_2.frame) == 1]):

            if info_annotator_1.frame == info_annotator_2.frame:

                text_anno_1 = info_annotator_1.predicate['text']
                text_anno_2 = info_annotator_2.predicate['text']

                if text_anno_1 == text_anno_2:
                    frame_label = list(info_annotator_1.frame)[0]
                    predicate_label = text_anno_1


                    lexeme_obj = Lexeme(lexeme=predicate_label,
                                        frame_label=frame_label,
                                        provenance=provenance_label)

                    frame_label2lexeme_obj[frame_label].append(lexeme_obj)
                    merging_stats['# of same frame annotations'] += 1

                else:
                    if verbose >= 2:
                        print()
                        print(key)
                        print('predicate label differs')
                        print(text_anno_1, text_anno_2)


    if verbose:
        print()
        print(f'num of frames with at least one annotation: {len(frame_label2lexeme_obj)}')
        print(merging_stats)

    return (frame_label2lexeme_obj, merging_stats)
import dfn_classes
import pickle

fn_obj = pickle.load(open('../output/dfn_objects/combined.p',
                          'rb'))

fn_obj.create_lexicon_data_annotation_tool(path_readme='../documentation/lexicon_data_for_frame_annotation_tool/README.md',
                                           path_ud_information='../documentation/lexicon_data_for_frame_annotation_tool/part_of_speech_ud_info.json',
                                           path_mapping_ud_pos_to_fn_pos='../documentation/lexicon_data_for_frame_annotation_tool/ud_pos_to_fn_pos.json',
                                           output_folder='../output/lexicon_data_for_frame_annotation_tool',
                                           verbose=2)

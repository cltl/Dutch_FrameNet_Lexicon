import pickle
import load_utils
import random

load_utils.load_python_module(module_path='../resources/ODWN_Reader',
                              module_name='odwn_classes', verbose=0)


def preprocess_dfn(fn_object_path):
    """
    Extract information from Dutch FrameNet
    for the computation of descriptive statistics.

    :param str fn_object_path: path to the version of Dutch FrameNet

    :rtype: tuple
    :return:    (fn_lu_id_pos2rbn_senseids,     dict for (FN LU id, POS) -> RBN LU id(s)
                rbn_senseid_pos2fn_lu_ids,      dict for (RBN LU id, POS) -> FN LU id(s)
                pos_set_fn,                     set for encountered POS in FN
                pos_set_rbn,                    set for encountered POS in RBN
                frame_label_pos2fn_lu_ids,      dict for (frame, None) -> FN LU id(s)
                frame_label_pos2rbn_senseids)   dict for (frame, None) -> RBN LU id(s)
    """
    with open(fn_object_path, 'rb') as infile:
        fn_obj = pickle.load(infile)

    pos_set_fn = set()
    pos_set_rbn = set()
    fn_lu_id_pos2rbn_senseids = dict()
    rbn_senseid_pos2fn_lu_ids = dict()
    frame_label_pos2fn_lu_ids = dict()
    frame_label_pos2rbn_senseids = dict()

    for frame_label, frame_obj in fn_obj.framelabel2frame_obj.items():
        for lu_id, lu_obj in frame_obj.lu_id2lu_obj.items():
            if lu_obj.rbn_senses:
                for rbn_dict in lu_obj.rbn_senses:
                    rbn_obj = rbn_dict['rbn_obj']

                    # update (FN LU id, POS) -> RBN LU id(s) dictionary
                    pos_set_fn.add(lu_obj.pos)
                    fn_lu_id_pos = (lu_id, lu_obj.pos)
                    if fn_lu_id_pos not in fn_lu_id_pos2rbn_senseids.keys():
                        fn_lu_id_pos2rbn_senseids[fn_lu_id_pos] = set()
                    fn_lu_id_pos2rbn_senseids[fn_lu_id_pos].add(rbn_obj.sense_id)

                    # update (RBN LU id, POS) -> FN LU id(s) dictionary
                    pos_set_rbn.add(rbn_obj.fn_pos)
                    rbn_senseid_pos = (rbn_obj.sense_id, rbn_obj.fn_pos)
                    if rbn_senseid_pos not in rbn_senseid_pos2fn_lu_ids.keys():
                        rbn_senseid_pos2fn_lu_ids[rbn_senseid_pos] = set()
                    rbn_senseid_pos2fn_lu_ids[rbn_senseid_pos].add(lu_id)


                    frame_label_pos = (frame_label, None) # POS is not an attribute of a frame

                    # update (frame, None) -> FN LU(s) dictionary
                    if frame_label_pos not in frame_label_pos2fn_lu_ids.keys():
                        frame_label_pos2fn_lu_ids[frame_label_pos] = set()
                    frame_label_pos2fn_lu_ids[frame_label_pos].add(lu_id)

                    # update (frame, None) -> RBN LU(s) dictionary
                    if frame_label_pos not in frame_label_pos2rbn_senseids.keys():
                        frame_label_pos2rbn_senseids[frame_label_pos] = set()
                    frame_label_pos2rbn_senseids[frame_label_pos].add(rbn_obj.sense_id)

    return fn_lu_id_pos2rbn_senseids, rbn_senseid_pos2fn_lu_ids, pos_set_fn, pos_set_rbn, frame_label_pos2fn_lu_ids, frame_label_pos2rbn_senseids


def create_evaluation_set(rbn_senseid_pos2fn_lu_ids, evaluation_set_path, proportion=1.0, verbose=0):
    """
    Create a subset of RBN LU ids linked to their corresponding FrameNet LU id(s)
    for manual evaluation, balanced for POS occurrences of RBN LU.

    :param dict rbn_senseid_pos2fn_lu_ids: (RBN LU id, POS) -> FN LU id(s)
    :param str evaluation_set_path: path to save the evaluation set to
    :param float proportion: proportion to compute sample size per POS, default 1.0 (full set)

    :rtype: NoneType
    :return: None, the evaluation set is written to .p file
    """
    if verbose:
        print('Creating manual evaluation subset')
    # categorize RBN senseids per POS
    pos2rbn_senseid2fn_lu_ids = dict()
    for rbn_senseid_pos, fn_lu_ids in rbn_senseid_pos2fn_lu_ids.items():
        rbn_senseid, pos = rbn_senseid_pos
        if pos not in pos2rbn_senseid2fn_lu_ids.keys():
            pos2rbn_senseid2fn_lu_ids[pos] = dict()
        pos2rbn_senseid2fn_lu_ids[pos][rbn_senseid] = fn_lu_ids

    # randomly sample per POS
    manual_evaluation_set = dict()
    for pos, rbn_senseid2fn_lu_ids in pos2rbn_senseid2fn_lu_ids.items():
        sample_size = round(len(rbn_senseid2fn_lu_ids)*proportion)
        if verbose:
            print(f'Total RBN senseids with POS {pos}: {len(rbn_senseid2fn_lu_ids)}')
            print(f'Sample RBN senseids with POS {pos}: {sample_size}')

        random.seed(15)
        pos_sample = random.sample(rbn_senseid2fn_lu_ids.items(), sample_size)
        for rbn_senseid, fn_lu_ids in pos_sample:
            manual_evaluation_set[rbn_senseid] = fn_lu_ids

    with open(evaluation_set_path, 'wb') as outfile:
        pickle.dump(manual_evaluation_set, outfile)
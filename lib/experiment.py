import experiment_utils
from stats_utils import compute_stats
from stats_utils import compute_stats_includingpos
import json
config_path = '../input/config_files/v1.json'
configuration = json.load(open(config_path))
verbose=1

# preprocess Dutch FrameNet
fn_lu_id_pos2rbn_senseids, rbn_senseid_pos2fn_lu_ids, pos_set_fn, pos_set_rbn, frame_label_pos2fn_lu_ids, frame_label_pos2rbn_senseids = experiment_utils.preprocess_dfn(configuration["fn_object_path"])

# compute RBN<->FN statistics
compute_stats_includingpos(fn_lu_id_pos2rbn_senseids,
                           ['Number of FrameNet LUs', 'Total number of links'],
                           f'{configuration["iteration_output_path"]}/luid2senseids_typetoken.txt',
                           ['FrameNet LU in-degree', 'Frequency'],
                           f'{configuration["iteration_output_path"]}/luid2senseids_ambiguity.txt',
                           pos_set_fn)
compute_stats_includingpos(rbn_senseid_pos2fn_lu_ids,
                           ['Number of RBN LUs', 'Total number of links'],
                           f'{configuration["iteration_output_path"]}/senseid2luids_typetoken.txt',
                           ['RBN LU out-degree', 'Frequency'],
                           f'{configuration["iteration_output_path"]}/senseid2luids_ambiguity.txt',
                           pos_set_rbn)

# compute frame to FN-RBN statistics
compute_stats(frame_label_pos2fn_lu_ids,
              ['Number of frames', 'Number of FrameNet LUs'],
              f'{configuration["iteration_output_path"]}/frame2luids_typetoken.txt',
              ['FrameNet LUs per frame', 'Number of frames'],
              f'{configuration["iteration_output_path"]}/frame2luids_ambiguity.txt')
compute_stats(frame_label_pos2rbn_senseids,
              ['Number of frames', 'Number of RBN LUs'],
              f'{configuration["iteration_output_path"]}/frame2senseids_typetoken.txt',
              ['RBN LUs per frame', 'Number of frames'],
              f'{configuration["iteration_output_path"]}/frame2senseids_ambiguity.txt')

# manual evaluation set
if configuration["create_evaluation_set"] == True:
    experiment_utils.create_evaluation_set(rbn_senseid_pos2fn_lu_ids, configuration["evaluation_set_path"], proportion=configuration["evaluation_set_proportion"], verbose=verbose)
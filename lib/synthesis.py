import synthesis_utils
from stats_utils import compute_stats
from stats_utils import compute_stats_includingpos
verbose=1


# preprocess and compute statistics for FrameNet
fn_form2fn_lu_ids, pos_set, frame_label_pos2fn_lu_ids = synthesis_utils.preprocess_framenet(verbose=verbose)
compute_stats_includingpos(fn_form2fn_lu_ids,
                           ['Number of unique English forms', 'Total number of FrameNet LUs'],
                           '../output/synthesis/framenet/form2luids_typetoken.txt',
                           ['Ambiguity class', 'Frequency'],
                           '../output/synthesis/framenet/form2luids_ambiguity.txt',
                           pos_set)
compute_stats(frame_label_pos2fn_lu_ids,
              ['Number of frames', 'Number of FrameNet LUs'],
              '../output/synthesis/framenet/frame2luids_typetoken.txt',
              ['FrameNet LUs per frame', 'Number of frames'],
              '../output/synthesis/framenet/frame2luids_ambiguity.txt')

# preprocess and compute statistics for Wiktionary
if verbose:
    print('Wiktionarigheid... veuillez patienter svp')
nl_pos2en, en_pos2nl = synthesis_utils.preprocess_wiki()
compute_stats(nl_pos2en,
              ['Number of unique Dutch forms', 'Total number of translation pairs'],
              '../output/synthesis/wiktionary/nl2en_typetoken.txt',
              ['Ambiguity class', 'Frequency'],
              '../output/synthesis/wiktionary/nl2en_ambiguity.txt')
compute_stats(en_pos2nl,
              ['Number of unique English forms', 'Total number of translation pairs'],
              '../output/synthesis/wiktionary/en2nl_typetoken.txt',
              ['Ambiguity class', 'Frequency'],
              '../output/synthesis/wiktionary/en2nl_ambiguity.txt')

# preprocess and compute statistics for RBN
rbn_form2rbn_senseids, pos_set = synthesis_utils.preprocess_rbn()
compute_stats_includingpos(rbn_form2rbn_senseids,
                           ['Number of unique Dutch forms', 'Total number of RBN LUs'],
                           '../output/synthesis/rbn/form2senseids_typetoken.txt',
                           ['Ambiguity class', 'Frequency'],
                           '../output/synthesis/rbn/form2senseids_ambiguity.txt',
                           pos_set)


# TODO: preprocess WordNet and compute stats (including POS)


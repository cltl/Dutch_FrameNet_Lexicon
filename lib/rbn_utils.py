from collections import defaultdict
import load_utils

stats_utils = load_utils.load_python_module(module_path='../resources/FN_Reader',
                                            module_name='stats_utils',
                                            verbose=1)

def load_frame2rbn_objs_via_subsumes_relation(fn, mapping, rbn_objs, verbose=0):
    """
    load the mapping from rbn to framenet as a relationship between

    frame -> every rbn lexical entry that is linked via a feature set match
    with a frame in fn
    """
    g = stats_utils.load_frame_relations_as_directed_graph(fn, subset_of_relations={'Inheritance'})

    # load mapping feature set to all fn frames that are under top frame
    rbn_featureset2all_frames = dict()
    for feature_set, top_frames in mapping.items():
        all_frames = set()
        for top_frame in top_frames:

            all_frames.add(top_frame)
            level2children = stats_utils.get_all_successors_of_all_successors(g,
                                                                              starting_node=top_frame,
                                                                              verbose=verbose)
            for depth, frames in level2children.items():
                all_frames.update(frames)

        rbn_featureset2all_frames[feature_set] = all_frames

    # load mapping feature set to all rbn lexical entries that have this feature set label
    feature_set2rbn_objs = defaultdict(list)
    for rbn_obj in rbn_objs:
        if rbn_obj.rbn_feature_set is not None:
            feature_set2rbn_objs[rbn_obj.rbn_feature_set].append(rbn_obj)

    # convert it into mapping from frame to all rbn lexical entries that are possible via subsumes relation
    frame2rbn_objs = defaultdict(list)
    frame2feature_set_values = defaultdict(set)

    for feature_set, all_frames in rbn_featureset2all_frames.items():
        rbn_objs = feature_set2rbn_objs[feature_set]
        for frame in all_frames:
            frame2rbn_objs[frame].extend(rbn_objs)
            frame2feature_set_values[frame].add(feature_set)

    return frame2rbn_objs, frame2feature_set_values
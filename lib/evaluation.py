import os
import sys
import pickle
from shutil import rmtree

import graph_utils

import networkx as nx

def create_svg_from_rbn_sense_to_fn_frame(rbn_sense,
                                          fn_lu,
                                          g,
                                          output_folder,
                                          verbose=0):
    """

    :param str rbn_sense: RBN sense as represented in the graph, e.g, '(pm)RBN-propvol-a-1'
    :param str fn_lu: identifier of English Framenet LU, e.g., LU-7016
    :param networkx.classes.graph.Graph g: graph containing all links
    between lexical resources, probably stored in
    -../output/dfn_objects/g.p
    -../output/dfn_objects/g_v1.p
    -etc.
    :return:
    """
    output_path_without_svg = f'{output_folder}/{fn_lu}'
    from_node = rbn_sense
    to_node = fn_lu

    all_paths = []

    # RBN to FN LUs
    assert from_node in g, f'{from_node} not found in graph'
    assert to_node in g, f'{to_node} not found in graph'

    # path from RBN sense to English FN LU node
    paths = nx.all_simple_paths(g,
                                source=from_node,
                                target=to_node,
                                cutoff=2)
    all_paths.extend(paths)

    # FN LU to Frame
    frame_node = g.nodes[to_node]['attr']['frame_short_rdf_uri']
    all_paths.append([to_node, frame_node])

    graph_utils.subgraph_in_dot(g,
                                all_paths,
                                output_path=output_path_without_svg,
                                verbose=verbose)

    if verbose >= 2:
        print()
        print(f'stored svg image at {output_path_without_svg}.svg')

def create_svg_folder_rbn_sense_to_fn_lus(output_folder,
                                          graph_path,
                                          path_rbn_to_lu,
                                          verbose=0):
    """

    :param str output_folder: path to output folder (will be removed if exists)
    :param networkx.classes.graph.Graph graph_path: graph containing all links
    between lexical resources, probably stored in
    -../output/dfn_objects/g.p
    -../output/dfn_objects/g_v1.p
    -etc.
    :param str path_rbn_to_lu: path to mapping from RBN sense to FN LU ids, e.g,
     'r_n-38434': {'LU-5962'}, 'r_n-31138': {'LU-5962'}
    """
    if os.path.exists(output_folder):
        rmtree(output_folder)
    os.mkdir(output_folder)

    g = nx.read_gpickle(graph_path)
    rbn_sense_to_fn_lu = pickle.load(open(path_rbn_to_lu, 'rb'))

    sense_id_to_sense_label = {}
    for node in g.nodes():
        if node.startswith('(pm)RBN-'):
            sense_id = g.nodes[node]['attr']['sense_id']
            sense_id_to_sense_label[sense_id] = node

    svgs = 0
    for rbn_sense, set_of_lu_ids in rbn_sense_to_fn_lu.items():
        lu_ids = list(set_of_lu_ids)
        assert len(lu_ids) == 1
        lu_id = lu_ids[0]

        create_svg_from_rbn_sense_to_fn_frame(rbn_sense=sense_id_to_sense_label[rbn_sense],
                                              fn_lu=lu_id,
                                              g=g,
                                              output_folder=output_folder,
                                              verbose=verbose)
        svgs += 1

    if verbose >= 1:
        print()
        print(f'output folder: {output_folder}')
        print(f'added {svgs} images to output folder.')


if __name__ == '__main__':
    create_svg_folder_rbn_sense_to_fn_lus(output_folder='../output/annotation/v1',
                                          graph_path='../output/dfn_objects/graph_v1.p',
                                          path_rbn_to_lu='../development/rbn_senseid2fn_lu_ids.p',
                                          verbose=1)
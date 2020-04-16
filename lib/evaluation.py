import json
from pathlib import Path
import pickle
from shutil import rmtree
import subprocess

import graph_utils

import networkx as nx

def create_svg_from_rbn_sense_to_fn_frame(rbn_sense,
                                          fn_lu,
                                          g,
                                          index,
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
    :param int index: used a basename for output path
    :param output_folder: output folder
    :return:
    """
    output_path_without_svg = f'{output_folder}/{index}'
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

def create_annotation_folder(output_folder,
                             graph_path,
                             path_rbn_to_lu,
                             overwrite=False,
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
    output_folder = Path(output_folder)

    if overwrite:
        if output_folder.exists():
            rmtree(str(output_folder))

    images_folder = output_folder.joinpath('images')
    annotations_folder = output_folder.joinpath('annotations')
    if not output_folder.exists():
        output_folder.mkdir(parents=True)
        images_folder.mkdir()
        annotations_folder.mkdir()

    g = nx.read_gpickle(graph_path)
    rbn_sense_to_fn_lu = pickle.load(open(path_rbn_to_lu, 'rb'))

    sense_id_to_sense_label = {}
    for node in g.nodes():
        if node.startswith('(pm)RBN-'):
            sense_id = g.nodes[node]['attr']['sense_id']
            sense_id_to_sense_label[sense_id] = node

    index_to_edge = {}
    index_to_annotation = {}
    for index, (rbn_sense,
                set_of_lu_ids) in enumerate(rbn_sense_to_fn_lu.items(), 1):
        lu_ids = list(set_of_lu_ids)
        assert len(lu_ids) == 1
        lu_id = lu_ids[0]

        create_svg_from_rbn_sense_to_fn_frame(rbn_sense=sense_id_to_sense_label[rbn_sense],
                                              fn_lu=lu_id,
                                              g=g,
                                              index=index,
                                              output_folder=images_folder,
                                              verbose=verbose)
        index_to_edge[index] = [rbn_sense, lu_id]
        index_to_annotation[index] = False

    assert len(index_to_edge) == len(rbn_sense_to_fn_lu), \
        f'mismatch between input dict (size {len(sense_id_to_sense_label)}\
          and number of svgs {len(index_to_edge)}'


    for a_dict, path in [(index_to_edge, annotations_folder / 'id_to_edge.json'),
                         (index_to_annotation, annotations_folder / 'annotations.json')]:
        with open(path, 'w') as outfile:
            json.dump(a_dict, outfile)

    if verbose >= 1:
        print()
        print(f'output folder: {output_folder}')
        print(f'stored svgs in {images_folder}')
        print(f'stored annotation input in {annotations_folder}')
        print(f'added {len(index_to_edge)} images to output folder.')

if __name__ == '__main__':
    create_annotation_folder(output_folder='../output/iteration1/tool_input',
                             graph_path='../output/dfn_objects/graph_v1.p',
                             path_rbn_to_lu='../development/rbn_senseid2fn_lu_ids.p',
                             overwrite=True,
                             verbose=1)
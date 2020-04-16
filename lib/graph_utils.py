from collections import defaultdict
import networkx as nx
import graphviz as gv
from graphviz import Source
import nltk


def load_graph(frame_label2frame_obj, synset_id2synset_obj, rbn_objs, options, verbose=0):
    """

    """
    g = nx.Graph()

    for frame_label, frame_obj in frame_label2frame_obj.items():

        frame_short_rdf_uri = frame_obj.short_rdf_uri
        assert frame_short_rdf_uri
        g.add_node(frame_short_rdf_uri, attr=frame_obj.get_hover_info())  # node is added

        if options['frame_en2lu_en']:
            for lu_id, lu_obj in frame_obj.lu_id2lu_obj.items():
                g.add_node(lu_id, attr=lu_obj.get_hover_info())  # node is added
                g.add_edge(frame_short_rdf_uri, lu_id)

        if options['lu_id2lemmapos_nl']:
            for lemma_obj in frame_obj.lemma_objs:
                lemmapos_nl = lemma_obj.short_rdf_uri
                g.add_node(lemmapos_nl, attr=lemma_obj.get_hover_info())  # node is added
                lu_id = lemma_obj.lu_id
                if lemma_obj.provenance == 'wiktionary':
                    g.add_edge(lemmapos_nl, lu_id)
                if lemma_obj.provenance == 'sonar_fn_annotations':
                    g.add_edge(lemmapos_nl, frame_short_rdf_uri)

        if options['rbn_les2feature_set2frame']:
            for rbn_obj in frame_obj.sense_objs:
                if rbn_obj.rbn_feature_set is not None:
                    g.add_edge(rbn_obj.short_rdf_uri, rbn_obj.rbn_feature_set)
                    g.add_edge(rbn_obj.rbn_feature_set, frame_short_rdf_uri)

    if options['rbn_les2lemma_pos_nl']:
        lemmapos2le_ids = defaultdict(set)
        for rbn_obj in rbn_objs:
            g.add_node(rbn_obj.short_rdf_uri, attr=rbn_obj.get_hover_info())  # node is added
            lemmapos_nl = f'(Dutch){rbn_obj.lemma}.{rbn_obj.fn_pos}'
            lemmapos2le_ids[lemmapos_nl].add(rbn_obj.short_rdf_uri)

        for lemmapos_nl, le_ids in lemmapos2le_ids.items():
            for le_id in le_ids:
                g.add_edge(lemmapos_nl, le_id)

    if options['synset2rbn']:
        for synset_id, synset_obj in synset_id2synset_obj.items():
            synset_id = synset_obj.synset_id
            g.add_node(synset_id, attr=synset_obj.get_hover_info()) # node is added

            for rbn_obj in synset_obj.synonyms:
                color = 'orange'
                if 'cdb2.2_Manual' in rbn_obj.provenance_set:
                    color = 'green'
                edge_attr = {'color' : color, 'tooltip' : rbn_obj.provenance_label}
                g.add_edge(synset_id, rbn_obj.short_rdf_uri, attr=edge_attr)

    if verbose:
        print(nx.info(g))
    return g


def create_hover_text(node_attributes, only_use=set()):
    """
    create string of node attributes

    :param dict node_attributes: a dict such as:
    {'attr': {'pos': None,
              'lemma': 'demonstratie',
              'mw': False,
              'rbn_type': None,
              'rbn_feature_set': None}
              }
    :param set only_use: if set is not empty, only these attributes will be used.

    :rtype: str
    :return: string representation, every attribute key on new line
    """
    info = []
    for key, value in node_attributes['attr'].items():

        if only_use:
            if key in only_use:
                info.append(f'{key}: {value}')

        else:
            info.append(f'{key}: {value}')

    return '\n'.join(info)


def get_paths_from_rbn_to_fn(g,
                             from_prefix,
                             to_prefix,
                             from_suffix=None,
                             to_suffix=None,
                             maximum_length_path=3,
                             verbose=0):
    """

    :param networkx.classes.graph.Graph g: an undirected graph
    :param str from_prefix: paths from all nodes that start with ...
    :param str to_prefix: paths to all nodes that start with ...
    :param int maximum_length_path: maximum path length (edge counting)
    :param int verbose: 0 no info, 1 general info

    :rtype: list
    :return: list of paths linking t
    """
    from_nodes = {node
                  for node in g.nodes()
                  if str(node).startswith(from_prefix)}

    to_nodes = {node
                for node in g.nodes()
                if str(node).startswith(to_prefix)}

    if from_suffix:
        from_nodes = {node
                      for node in from_nodes
                      if node.endswith(from_suffix)}

    if to_suffix:
        to_nodes = {node
                    for node in to_nodes
                    if node.endswith(to_suffix)}

    if verbose:
        print('# of from nodes', len(from_nodes))
        print('# of to nodes', len(to_nodes))

    all_paths = []
    for from_node in from_nodes:
        if verbose >= 2:
            print(from_node)
        for to_node in to_nodes:
            try:
                paths = nx.all_simple_paths(g,
                                            source=from_node,
                                            target=to_node,
                                            cutoff=maximum_length_path)
                for path in paths:
                    all_paths.append(path)
            except nx.NetworkXNoPath:
                continue

    if verbose:
        print(f'number of paths found between {from_prefix} to {to_prefix} nodes', len(all_paths))

    return all_paths


def subgraph_in_dot(g,
                    paths,
                    add_synset_edges=False,
                    add_rbn_feature_set=False,
                    output_path=None,
                    verbose=0):
    """
    load the paths as graphviz object such that we can easily vizualize it

    :param networkx.classes.graph.Graph g: an undirected graph
    :param list paths: list of lists, each list representing a path in the graph
    :param str output_path: if provided, the graph will be saved to that path

    :rtype: graphviz.dot.Graph
    :return: the graph as graphviz object
    """
    lemma_g = gv.Graph()

    nodes = dict()
    edges = dict()

    # find unique nodes and edges
    for path in paths:
        for source, target in nltk.bigrams(path):
            nodes[source] = dict()
            nodes[target] = dict()
            edges[(source, target)] = dict()

    if verbose >= 2:
        print()
        print(f'# of nodes: {len(nodes)}')
        print(f'# of edges: {len(edges)}')

    # add nodes to graph
    for node in list(nodes): # nodes is a list here because else the dictionary would change size during the for loop
        # add edge to frame
        if node.startswith(f'(pm)fn1.7'):
            frame_attr = g.node[node]

            # add edge to RBN feature set
            if add_rbn_feature_set:
                for rbn_feature_set in frame_attr['attr']['rbn_feature_set_values']:
                    edges[(node, rbn_feature_set)] = dict() # edge added

        if node.startswith('(pm)RBN-'):
            node_attr = g.node[node]
            feature_set_value = node_attr['attr']['rbn_feature_set']
            if all([feature_set_value is not None,
                    feature_set_value]):
                edges[(node, feature_set_value)] = dict() # edge added

            if add_synset_edges:
                synset_id = node_attr['attr']['synset_id']
                if synset_id is not None:
                    edge_attr = g.get_edge_data(node, synset_id)
                    if edge_attr is None:
                        print('no edge attr between', node, synset_id)
                        edges[(node, synset_id)] = dict()
                    else:
                        edges[(node, synset_id)] = edge_attr['attr'] # edge added
                    nodes[synset_id] = dict() # node added

                    if not g.has_node(synset_id):
                        print(f'synset not found: {synset_id}')
                    else:
                        synset_info = g.node[synset_id]
                        for synonym in synset_info['attr']['synonyms']:
                            if synonym != node:
                                edges[(synonym, synset_id)] = dict() # edge added
                                nodes[synonym] = dict() # node added


    # add nodes to graph
    for node in nodes:
        if not g.has_node(node):
            print(f'node {node} not in graph')
        else:
            hover_text = create_hover_text(g.node[node])
            lemma_g.node(node, tooltip=hover_text)

    # add edges to graph
    for (source, target), attributes in edges.items():
        lemma_g.edge(source, target, _attributes=attributes)

    lemma_g.format = 'svg'

    if output_path is not None:
        lemma_g.render(output_path)

    return lemma_g

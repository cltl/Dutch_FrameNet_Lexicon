from rdflib import ConjunctiveGraph, Graph


def load_nquads_file(path_to_nquad_file):
    """
    load rdf file in nquads format

    :param str path_to_nquad_file: path to rdf file in nquad format


    :rtype: rdflib.graph.ConjunctiveGraph
    :return: nquad

    """
    g = ConjunctiveGraph()
    with open(path_to_nquad_file, "rb") as infile:
        g.parse(infile, format="nquads")
    return g

def convert_nquads_to_nt(g, output_path):
    """

    :param rdflib.graph.ConjunctiveGraph g: a nquad graph

    :rtype:
    :return:
    """
    g.serialize(destination=output_path, format='nt')

def load_nt_graph(nt_path):
    g = Graph()
    with open(nt_path, 'rb') as infile:
        g.parse(file=infile, format='nt')

    return g
if __name__ == '__main__':
    # should exist after running install.sh
    path = 'resources/premon/premon-2018a-fn17-noinf.tql'
    g = load_nquads_file(path_to_nquad_file=path)
    convert_nquads_to_nt(g, output_path='resources/premon/premon-2018a-fn17-noinf.nt')
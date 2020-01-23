from collections import Counter
import shutil
import os
import json
from lxml import etree


def get_rdf_label(graph, uri):
    query = """SELECT ?o WHERE {
        <%s> rdfs:label ?o
    }"""
    the_query = query % uri

    results = graph.query(the_query)

    labels = set()
    for result in results:
        label = str(result.asdict()['o'])
        labels.add(label)

    assert len(labels) == 1, f'expected one label for {uri}, got {labels}'

    return labels.pop()


def fn_pos2wn_pos(fn_pos):
    """
    FrameNet part of speech to WordNet part of speech

    :param str fn_pos: FrameNet part of speech

    :rtype: str
    :return: WordNet part of speech or None if not mapped
    """

    if fn_pos == 'A':
        wn_pos = 'a'
    elif fn_pos == 'V':
        wn_pos = 'v'
    elif fn_pos == 'ADV':
        wn_pos = 'r'
    elif fn_pos == 'N':
        wn_pos = 'n'
    elif fn_pos in {'ART',
                    'C',
                    'IDIO',
                    'INTJ',
                    'NUM',
                    'PREP',
                    'PRON',
                    'SCON'}:
        wn_pos = 'UNMAPPABLE'
    else:
        raise AssertionError(f'{fn_pos} not part of FN pos tagset')

    return wn_pos


assert fn_pos2wn_pos('V') == 'v'
assert fn_pos2wn_pos('N') == 'n'
assert fn_pos2wn_pos('A') == 'a'
assert fn_pos2wn_pos('ART') == 'UNMAPPABLE'


def filter_based_on_spaces_in_lemma(lemma_objs, verbose=0):
    """
    :param list lemma_objs: list of dfn_classes.Lemma objects
    """
    filtered_lemma_objs = []

    for lemma_obj in lemma_objs:
        if ' ' not in lemma_obj.lemma:
            filtered_lemma_objs.append(lemma_obj)
        else:
            if verbose >= 2:
                print(f'skipping {lemma_obj.lemma} because it contains spaces')

    return filtered_lemma_objs


def filter_based_on_rbn(lemma_objs, rbn_objs, verbose=0):
    """

    :param list lemma_objs: list of dfn_classes.Lemma objects
    :param list rbn_objs: list of resources.RBN_Reader.rbn_classes.LE objects
    """
    rbn_lemmas = {rbn_obj.lemma
                  for rbn_obj in rbn_objs}
    rbn_lemma_pos = {(rbn_obj.lemma, rbn_obj.fn_pos)
                     for rbn_obj in rbn_objs}

    filtered_lemma_objs = []

    for lemma_obj in lemma_objs:

        if lemma_obj.pos:
            if (lemma_obj.lemma, lemma_obj.pos) in rbn_lemma_pos:
                filtered_lemma_objs.append(lemma_obj)
            else:
                if verbose >= 2:
                    print(f'ignoring because not in RBN {lemma_obj.lemma, lemma_obj.pos}')

        else:
            if lemma_obj.lemma in rbn_lemmas:
                filtered_lemma_objs.append(lemma_obj)
            else:
                if verbose >= 2:
                    print(f'ignoring because not in RBN {lemma_obj.lemma}')

    return filtered_lemma_objs


class FrameNet:
    """

    """
    def __init__(self):
        self.framelabel2frame_obj = {}


        self.cur_dutch_lemma_pos_id = 0
        self.dutch_lemma_pos2id = {}


    def __str__(self):
        info = [f'num of frames: {len(self.framelabel2frame_obj)}']

        return '\n'.join(info)

    def update_lemma_obj_with_lemmapos_id(self, lemma_obj):
        """
        provided that a Lemma object has:
        -a lemma
        -a FrameNet part of speech

        this method updates the attribute lemma_pos_id with an identifier
        :param Lemma lemma_obj:
        """
        assert lemma_obj.language == 'Dutch', f'language of {lemma_obj.get_short_uri()} should be Dutch (English lemma,pos combination should already have lemmma_pos_id)'
        if all([lemma_obj.lemma is not None,
                lemma_obj.pos is not None]):

            key = (lemma_obj.lemma, lemma_obj.pos)

            if key in self.dutch_lemma_pos2id:
                lemma_obj.lemma_pos_id = self.dutch_lemma_pos2id[key]
            else:
                identifier = f'{lemma_obj.language}-{self.cur_dutch_lemma_pos_id}'
                lemma_obj.lemma_pos_id = identifier
                self.dutch_lemma_pos2id[(lemma_obj.lemma, lemma_obj.pos)] = lemma_obj.lemma_pos_id
                self.cur_dutch_lemma_pos_id += 1

    def validate_lemmapos_identifiers(self):
        identifiers = []
        for framelabel, frame_obj in self.framelabel2frame_obj.items():
            for lemma_obj in frame_obj.lemma_objs:
                if lemma_obj.lemma_pos_id is not None:
                    identifiers.append(lemma_obj.lemma_pos_id)

        assert len(set(identifiers)) == len(self.dutch_lemma_pos2id)


    def get_frame_to_info(self, verbose=0):
        """
        create frame PreMOn URI -> frame information, which will be used
        in the Frame Annotation Tool (https://github.com/cltl/frame-annotation-tool)
        """
        frame_rdf_uri_to_info = {}

        for frame_label, frame_obj in self.framelabel2frame_obj.items():

            frame_rdf_uri = frame_obj.rdf_uri

            fes = []
            for fe_obj in frame_obj.frame_elements:

                fe_info = {
                    'definition' : fe_obj.fe_definition,
                    'rdf_uri' : fe_obj.rdf_uri,
                    'fe_label' : fe_obj.fe_label,
                    'fe_type' : fe_obj.fe_type
                }
                fes.append(fe_info)

            info = {
                'definition' : frame_obj.definition,
                'frame_label' : frame_obj.frame_label,
                'framenet_url' : frame_obj.fn_url,
                'frame_elements' : fes
            }

            frame_rdf_uri_to_info[frame_rdf_uri] = info

        if verbose:
            print()
            print(f'found {len(frame_rdf_uri_to_info)} using method FrameNet.get_frame_to_info')

        return frame_rdf_uri_to_info


    def create_lexicon_data_annotation_tool(self,
                                            path_readme,
                                            path_ud_information,
                                            path_mapping_ud_pos_to_fn_pos,
                                            output_folder,
                                            verbose=0):
        """
        create a folder with FrameNet information to be used in the annotation tool

        :param str path_readme: path to read of the documents that it will contain, e.g.,
        documentation/lexicon_data_for_frame_annotation_tool/README.md
        :param str path_ud_information: JSON file mapping UD pos tag to more information about the label
        :param str path_mapping_ud_pos_to_fn_pos: JSON file mapping UD pos tag to FN pos tag
        :param str output_folder: where the folder should be stored, e.g., "lexicon_data_annotation_tool"
        """
        # recreate folder if needed
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
        os.mkdir(output_folder)

        # write readme
        output_path_readme = os.path.join(output_folder, 'README.md')
        shutil.copy(path_readme, output_path_readme)

        if verbose:
            print(f'written README to {output_path_readme}')

        # write UD information
        output_path_ud_information = os.path.join(output_folder, 'part_of_speech_ud_info.json')
        shutil.copy(path_ud_information, output_path_ud_information)

        if verbose:
            print(f'written UD information to {output_path_ud_information}')

        # write mapping UD pos to FN pos
        output_path_mapping_ud_fn = os.path.join(output_folder, 'ud_pos_to_fn_pos.json')
        shutil.copy(path_mapping_ud_pos_to_fn_pos, output_path_mapping_ud_fn)

        if verbose:
            print(f'written mapping UD to FN to {output_path_mapping_ud_fn}')

        # write frame_to_info
        frame_to_info = self.get_frame_to_info()
        output_path_frame_to_info = os.path.join(output_folder, 'frame_to_info.json')
        with open(output_path_frame_to_info, 'w') as outfile:
            json.dump(frame_to_info,
                      outfile,
                      indent=4,
                      sort_keys=True)

        if verbose:
            print(f'written frame_to_info to {output_path_frame_to_info}')


    def convert_to_nltk_package(self, english_fn_folder, output_folder):
        """
        the original English FrameNet folder is copied to 'output_folder'
        Then, for all frame files (xml files in frame folder),
        we remove all English lexical units and insert Dutch ones


        You can then load Dutch FrameNet using:

        from nltk.corpus.reader.framenet import FramenetCorpusReader
        fn_instance = FramenetCorpusReader(output_folder, ['frRelation.xml',
                                                           'frameIndex.xml',
                                                          'semTypes.xml'])

        :param str english_fn_folder: folder where English FrameNet is stored.
        Could be found at:
        >>> import nltk
        >>> import os
        >>> os.path.join(nltk.data.path[0], 'corpora', 'framenet_v17')
        :param str output_folder: where you would like to store Dutch FrameNet
        """
        namespaces = {'xmlns': 'http://framenet.icsi.berkeley.edu'}

        if os.path.exists(output_folder):
           shutil.rmtree(output_folder)
        shutil.copytree(src=english_fn_folder, dst=output_folder)

        for frame_label, frame_obj in self.framelabel2frame_obj.items():

            xml_input_path = os.path.join(english_fn_folder,
                                          'frame',
                                          f'{frame_label}.xml')
            assert os.path.exists(xml_input_path)
            parser = etree.XMLParser(remove_blank_text=True)
            doc = etree.parse(xml_input_path, parser)
            root = doc.getroot()

            for lu_el in doc.findall('xmlns:lexUnit', namespaces):
                lu_el.getparent().remove(lu_el)

            for lu_id, lu_obj in frame_obj.lu_id2lu_obj.items():
                if lu_obj.rbn_senses:
                    for rbn_sense in lu_obj.rbn_senses:
                        rbn_obj = rbn_sense['rbn_obj']
                        attr = {'status': rbn_sense['status'],
                                'POS': lu_obj.pos,
                                'name': f'{rbn_obj.lemma}.{rbn_obj.fn_pos}',
                                'ID': lu_obj.id_[3:],
                                'lemmaID': rbn_sense['lemmaID'],
                                'cBy': rbn_sense['provenance'],
                                'cDate': rbn_sense['cDate']
                                }
                        le_el = etree.Element('lexUnit', attrib=attr)

                        def_el = etree.Element('definition')
                        if rbn_obj.definition is None:
                            definition = 'NO DEFINITION'
                        else:
                            definition = rbn_obj.definition
                        def_el.text = definition
                        le_el.append(def_el)

                        sent_count_el = etree.Element('sentenceCount', attrib={
                            'annotate': '0',
                            'total': '0'
                        })
                        le_el.append(sent_count_el)

                        lexeme_el = etree.Element('lexeme', attrib={
                            'order': '1',
                            'headword': "false",
                            'breakBefore': "false",
                            'POS': lu_obj.pos,
                            'name': rbn_obj.lemma
                        })
                        le_el.append(lexeme_el)

                        root.append(le_el)

            output_path = os.path.join(output_folder,
                                       'frame',
                                       f'{frame_label}.xml')

            with open(output_path, 'w') as outfile:

                xml_string = etree.tostring(root,
                                            pretty_print=True,
                                            xml_declaration=True,
                                            encoding='utf-8')

                outfile.write(xml_string.decode('utf-8'))


class Frame:
    """

    """
    def __init__(self,
                 fn_frame_obj,
                 frame_label,
                 definition,
                 fn_version,
                 rdf_prefix,
                 fn_url,
                 premon_nt):
        self.frame_label = frame_label
        self.definition = definition
        self.fn_version = fn_version
        self.fn_url = fn_url
        self.rdf_uri = self.get_rdf_uri(premon_nt, frame_label)
        self.rdf_prefix_uri = self.get_rdf_prefix_colon_item(rdf_prefix)
        # TODO: FrameElement relations

        self.frame_elements = self.get_frame_elements(premon_nt=premon_nt,
                                                      fn_frame_obj=fn_frame_obj,
                                                      rdf_prefix=rdf_prefix)

        self.lemma_objs = []
        self.lexeme_objs = []
        self.rbn_feature_set_values = []

    def get_hover_info(self):
        return {
            'frame_label': self.frame_label,
            'definition': self.definition,
            'rbn_feature_set_values': self.rbn_feature_set_values
        }

    def get_fe_uris_and_labels(self, premon_nt, frame_uri):

        # get roles
        roles_of_frames = """SELECT ?o WHERE {
            <%s> <http://premon.fbk.eu/ontology/core#semRole> ?o
        }"""
        the_query = roles_of_frames % frame_uri

        results = premon_nt.query(the_query)

        label_to_fe_uri = dict()
        for result in results:
            fe_uri = str(result.asdict()['o'])

            label = get_rdf_label(premon_nt, fe_uri)
            label_to_fe_uri[label] = fe_uri

        return label_to_fe_uri

    def get_frame_elements(self, premon_nt, fn_frame_obj, rdf_prefix):
        fe_objs = []

        label_to_fe_uri = self.get_fe_uris_and_labels(premon_nt=premon_nt,
                                                      frame_uri=self.rdf_uri)

        for fe_label, fe in fn_frame_obj.FE.items():

            fe_rdf_uri = label_to_fe_uri[fe_label]
            fe_obj = FrameElement(fn_fe_obj=fe,
                                  rdf_prefix=rdf_prefix,
                                  rdf_uri=fe_rdf_uri)
            fe_objs.append(fe_obj)

        return fe_objs

    def get_rdf_uri(self, premon_nt, frame_label):
        frame_query = """SELECT ?s WHERE {
            ?s rdf:type <http://premon.fbk.eu/ontology/fn#Frame> .
            ?s rdfs:label "%s" .
        }"""
        the_query = frame_query % frame_label
        results = [result
                   for result in premon_nt.query(the_query)]

        assert len(results) == 1, f'query should only have one result: {the_query}\n{results}'

        for result in results:
            frame_rdf_uri = str(result.asdict()['s'])

        return frame_rdf_uri

    def get_rdf_prefix_colon_item(self, rdf_prefix):
        item = self.rdf_uri.split('/')[-1]
        return f'{rdf_prefix}:{item}'

    def add_lu_objs(self, frame, frame_short_rdf_uri):
        self.lu_id2lu_obj = dict()
        for lemma_pos, lu_info in frame.lexUnit.items():
            lu_obj = LU(lu_info, frame_short_rdf_uri)
            self.lu_id2lu_obj[lu_obj.id_] = lu_obj

    def __str__(self):
        info = [f'Frame: {self.frame_label} ({self.rdf_uri})\n']
        info.append('LEXEMES (provenance FrameNet annotations on SoNaR):')
        info.append(','.join([lexeme_obj.lexeme
                    for lexeme_obj in self.lexeme_objs]))
        info.append('\n')

        info.append('LEMMAS (provenance Wiktionary and FrameNet annotations on SoNaR):')
        freq_dist = Counter([(lemma_obj.lemma, lemma_obj.pos)
                             for lemma_obj in self.lemma_objs])
        info.append(str(freq_dist))
        info.append('\n')


        info.append('LEMMAS (provenance Wiktionary):')
        for lu_id, lu_obj in self.lu_id2lu_obj.items():
            freq_dist = Counter([(lemma_obj.lemma)
                                 for lemma_obj in self.lemma_objs
                                 if all([lemma_obj.lu_id == lu_id,
                                         lemma_obj.provenance == 'wiktionary'])
                                 ])
            info.append(f'{lu_id} ({lu_obj.lexeme}): {str(freq_dist)}')
            rbn_senses = []
            if hasattr(lu_obj, 'rbn2fn'):
                rbn_senses.extend(lu_obj.rbn2fn)
            if rbn_senses:
                info.append(f'RBN senses: {rbn_senses}\n')

        return '\n'.join(info)

class FrameElement:
    """

    """
    def __init__(self,
                 fn_fe_obj,
                 rdf_prefix,
                 rdf_uri):
        self.fn_fe_id = fn_fe_obj.ID   # the integer used by FrameNet as an identifier for the FrameElement
        self.fe_label = fn_fe_obj.name # the FrameElement label
        self.fe_type = fn_fe_obj.coreType # coretype: Core | Core-Unexpressed | Extra-Thematic | Peripheral
        self.fe_definition = fn_fe_obj.definition
        self.rdf_uri = rdf_uri
        self.rdf_prefix_uri = self.get_rdf_prefix_colon_item(rdf_prefix)

    def get_rdf_prefix_colon_item(self, rdf_prefix):
        item = self.rdf_uri.split('/')[-1]
        return f'{rdf_prefix}:{item}'

    def __str__(self):
        info = ['Frame Element:',
                f'FN ID: {self.fn_fe_id}',
                f'Label: {self.fe_label}',
                f'Type: {self.fe_type}',
                f'Definition: {self.fe_definition}']
        return '\n'.join(info)

class LU:
    """
    """
    def __init__(self, lu_info, frame_short_rdf_uri):
        self.id_ = f'LU-{lu_info.ID}'
        self.pos = lu_info.POS
        self.lexeme = self.get_lexeme(lu_info)
        self.frame_short_rdf_uri = frame_short_rdf_uri
        self.rbn_senses = []


    def get_hover_info(self):
        return {
            'pos' : self.pos,
            'lemma' : self.lexeme,
            'frame_short_rdf_uri' : self.frame_short_rdf_uri
        }

    def get_lexeme(self, lu_info):
        lexeme_parts = [lexeme_part['name']
                        for lexeme_part in lu_info.lexemes]
        lexeme = ' '.join(lexeme_parts)
        return lexeme

    def __str__(self):
        info = [f'ID: {self.id_}',
                f'POS: {self.pos}',
                f'LEMMA: {self.lexeme}',
                f'RBN senses: {self.rbn_senses}',
                f'frame_short_rdf_uri: {self.frame_short_rdf_uri}']
        return '\n'.join(info)

class Lemma:
    """

    """
    def __init__(self,
                 lemma,
                 frame_label,
                 provenance,
                 language,
                 pos=None,
                 lu_id=None):
        self.lemma = lemma
        self.frame_label = frame_label
        self.provenance = provenance
        self.language = language
        self.lu_id = lu_id
        self.pos = pos
        self.lemma_pos_id = None # FrameNet provides an identifier for each lemma and pos combination

        self.short_rdf_uri = self.get_short_uri()


    def get_hover_info(self):
        return {
            'lemma': self.lemma,
            'language' : self.language,
            'pos' : self.pos,
        }

    def get_short_uri(self):
        if self.pos is not None:
            uri = f'({self.language}){self.lemma}.{self.pos}'
        else:
            uri = f'({self.language}){self.lemma}'

        return uri


    def __str__(self):
        info = [f'frame label: {self.frame_label}',
                f'lemma: {self.lemma}',
                f'pos: {self.pos}',
                f'LU ID: {self.lu_id}',
                f'provenance: {self.provenance}']

        return ' '.join(info)

class Lexeme:
    """

    """
    def __init__(self, lexeme, frame_label, provenance):
        self.lexeme = lexeme
        self.frame_label = frame_label
        self.provenance = provenance


    def __str__(self):
        info = [f'frame label: {self.frame_label}',
                f'lexeme: {self.lexeme}',
                f'provenance: {self.provenance}']

        return ' '.join(info)




if __name__ == '__main__':
    import pickle
    fn_obj = pickle.load(open('output/combined.p', 'rb'))

    fn_obj.create_lexicon_data_annotation_tool(path_readme='documentation/lexicon_data_for_frame_annotation_tool/README.md',
                                               path_ud_information='documentation/lexicon_data_for_frame_annotation_tool/part_of_speech_ud_info.json',
                                               path_mapping_ud_pos_to_fn_pos='documentation/lexicon_data_for_frame_annotation_tool/ud_pos_to_fn_pos.json',
                                               output_folder='lexicon_data_for_frame_annotation_tool',
                                               verbose=2)


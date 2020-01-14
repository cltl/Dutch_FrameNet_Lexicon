from collections import Counter
import shutil
import os
from lxml import etree


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
                 frame_label,
                 definition,
                 fn_version,
                 rdf_prefix,
                 premon_nt):
        self.frame_label = frame_label
        self.definition = definition
        self.fn_version = fn_version
        self.rdf_uri = self.get_rdf_uri(premon_nt, frame_label)
        self.rdf_prefix_uri = self.get_rdf_prefix_colon_item(rdf_prefix)

        print(self.rdf_uri, self.rdf_prefix_uri)

        self.lemma_objs = []
        self.lexeme_objs = []
        self.rbn_feature_set_values = []

    def get_hover_info(self):
        return {
            'frame_label': self.frame_label,
            'definition': self.definition,
            'rbn_feature_set_values': self.rbn_feature_set_values
        }

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

class Role:
    """

    """

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
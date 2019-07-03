from collections import Counter


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


class EnFrame:
    """

    """
    def __init__(self,
                 frame_label,
                 definition,
                 namespace,
                 fn_version,
                 short_namespace):
        self.frame_label = frame_label
        self.definition = definition
        self.namespace = namespace
        self.fn_version = fn_version
        self.short_namespace = short_namespace

        self.lemma_objs = []
        self.lexeme_objs = []
        self.rbn_feature_set_values = []

    def get_hover_info(self):
        return {
            'frame_label': self.frame_label,
            'definition': self.definition,
            'rbn_feature_set_values': self.rbn_feature_set_values
        }

    def get_full_rdf_uri(self):
        return f'{self.namespace}fn{self.fn_version}-{self.frame_label.lower()}'

    def get_short_rdf_uri(self):
        return f'({self.short_namespace})fn{self.fn_version}-{self.frame_label.lower()}'

    def add_lu_objs(self, frame, frame_short_rdf_uri):
        self.lu_id2lu_obj = dict()
        for lemma_pos, lu_info in frame.lexUnit.items():
            lu_obj = LU(lu_info, frame_short_rdf_uri)
            self.lu_id2lu_obj[lu_obj.id_] = lu_obj

    def __str__(self):
        info = [f'Frame: {self.frame_label}\n']
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


class LU:
    """
    """

    def __init__(self, lu_info, frame_short_rdf_uri):
        self.id_ = f'LU-{lu_info.ID}'
        self.pos = lu_info.POS
        self.lexeme = self.get_lexeme(lu_info)
        self.frame_short_rdf_uri = frame_short_rdf_uri


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

from collections import Counter


class EnFrame:
    """

    """
    def __init__(self, frame_label):
        self.frame_label = frame_label
        self.lemma_objs = []
        self.lexeme_objs = []
        self.sense_objs = []


    def __str__(self):
        info = [f'Frame: {self.frame_label}\n']
        info.append('LEXEMES (provenance FrameNet annotations on SoNaR):')
        info.append(','.join([lexeme_obj.lexeme
                    for lexeme_obj in self.lexeme_objs]))
        info.append('\n')
        info.append('LEMMAS (provenance Wiktionary):')
        freq_dist = Counter([lemma_obj.lemma
                             for lemma_obj in self.lemma_objs])
        info.append(str(freq_dist))
        return '\n'.join(info)

class Lemma:
    """

    """
    def __init__(self, lemma, frame_label, provenance, lu_id=None):
        self.lemma = lemma
        self.frame_label = frame_label
        self.provenance = provenance
        self.lu_id = lu_id


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

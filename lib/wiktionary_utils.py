import pandas
from collections import defaultdict

def load_wiktionary(configuration, verbose=0):
    """
    load wiktionary translations for Dutch <-> English

    :param dict configuration: configuration (see config_files folder)

    :rtype: tuple
    :return: (nl2en,
              en2nl)
    """

    df = pandas.read_csv(configuration['wiktionary_translations_path'],
                         sep='\t', usecols=['ID', 'Concept_ID', 'Concept', 'Languoid', 'Language_name', 'Form'])


    if verbose:
        print()
        print('number of available languages', len(set(df.Language_name)))
        print('language that have Dutch in the name')
        for language in set(df.Language_name):
            if 'Dutch' in language:
                print(language)
        print('we use: Dutch; Flemish')

    df = df[df.Language_name == 'Dutch; Flemish']

    english_lemmas = []
    english_definitions = []

    for index, row in df.iterrows():
        concept = row['Concept']
        lemma, *definitions = concept.split('/')
        english_lemmas.append(lemma)
        english_definitions.append('/'.join(definitions))

    df['English_lemma'] = english_lemmas

    dutch2english = defaultdict(set)
    english2dutch = defaultdict(set)

    for index, row in df.iterrows():
        english_lemma = row['English_lemma']
        dutch_lemma = row['Form']
        dutch2english[dutch_lemma].add(english_lemma)
        english2dutch[english_lemma].add(dutch_lemma)

    if verbose:
        print(f'Dutch lemmas with English translations: {len(dutch2english)}')
        print(f'English lemmas with Dutch translations: {len(english2dutch)}')

    return dutch2english, english2dutch
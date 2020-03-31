import pandas


def load_combined_resources_as_df(fnlabel2fn_obj):
    """
    load instances of class EnFrame (see dfn_classes.py)
    into dataframe for computing descriptive statistics


    :param dict fnlabel2fn_obj: frame label -> instance of class EnFrame (see dfn_classes.py)

    :rtype: pandas.core.frame.DataFrame
    :return: df for computing statistics
    """
    list_of_lists = []
    headers = ['frame_label', 
               '# of unique lexemes', 
               '# of unique lemmas',
               '# of RBN senses']
    
    lu2number_of_dutch_senses = dict()

    for frame_label, frame_obj in fnlabel2fn_obj.items():
        unique_lexemes = set([lexeme_obj.lexeme
                              for lexeme_obj in frame_obj.lexeme_objs])

        unique_lemmas = set([lemma_obj.lemma
                             for lemma_obj in frame_obj.lemma_objs])
        
        number_of_rbn_senses = 0
        for lu_id, lu_obj in frame_obj.lu_id2lu_obj.items():
            
            num_of_lu_senses = 0
            if hasattr(lu_obj, 'rbn_senses'):
                num_of_lu_senses += len(lu_obj.rbn_senses)
                if lu_obj.rbn_senses:
                    for sense_id in lu_obj.rbn_senses:
                        number_of_rbn_senses += 1
            
            lu2number_of_dutch_senses[lu_id] = num_of_lu_senses

        one_row = [frame_label, len(unique_lexemes), len(unique_lemmas), number_of_rbn_senses]

        list_of_lists.append(one_row)

    df = pandas.DataFrame(list_of_lists, columns=headers)
    return df, lu2number_of_dutch_senses


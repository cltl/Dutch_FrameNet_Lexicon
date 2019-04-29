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
    headers = ['frame_label', '# of unique lexemes', '# of unique lemmas']
    for frame_label, frame_obj in fnlabel2fn_obj.items():
        unique_lexemes = set([lexeme_obj.lexeme
                              for lexeme_obj in frame_obj.lexeme_objs])

        unique_lemmas = set([lemma_obj.lemma
                             for lemma_obj in frame_obj.lemma_objs])

        one_row = [frame_label, len(unique_lexemes), len(unique_lemmas)]

        list_of_lists.append(one_row)

    df = pandas.DataFrame(list_of_lists, columns=headers)
    return df
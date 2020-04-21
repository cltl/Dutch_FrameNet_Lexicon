import pandas


def compute_stats(resource, typetoken_headers, typetoken_path, ambiguity_headers, ambiguity_path, pos={None}):
    """
    Compute descriptive statistics for a resource,
    convert to LaTeX tables and save to .txt files.

    :param dict resource: (form, POS) -> prevalence set
    :param list typetoken_headers: ['Type header', 'Token header']
    :param str typetoken_path: path to save the typetoken statistics to
    :param list ambiguity_headers: ['Ambiguity class', 'Frequency']
    :param str ambiguity_path: path to save the ambiguity statistics to
    :param set pos: POS to calculate the statistics for, default {None} (POS not applicable)

    :rtype: NoneType
    :return: None, the statistics are written to .txt files as LaTeX tables
    """
    # compute statistics
    type_observations = 0
    token_observations = 0
    ambiguity_dict = dict()
    for form, prevalence_set in resource.items():
        if form[1] in pos:
            type_observations += 1
            token_observations += len(prevalence_set)
            ambiguity_class = len(prevalence_set)
            if ambiguity_class not in ambiguity_dict.keys():
                ambiguity_dict[ambiguity_class] = 0
            ambiguity_dict[ambiguity_class] += 1

    # convert statistics to list_of_lists to dataframe to LaTeX

    typetoken_lol = list()
    typetoken = [type_observations, token_observations]
    typetoken_lol.append(typetoken)

    ambiguity_lol = list()
    for ambiguity_class, prevalence in sorted(ambiguity_dict.items()):
        one_row = [ambiguity_class, prevalence]
        ambiguity_lol.append(one_row)

    typetoken_df = pandas.DataFrame(typetoken_lol, columns=typetoken_headers)
    ambiguity_df = pandas.DataFrame(ambiguity_lol, columns=ambiguity_headers)

    typetoken_latex = typetoken_df.to_latex(index=False)
    ambiguity_latex = ambiguity_df.to_latex(index=False)
    with open (typetoken_path, 'w') as outfile:
        outfile.write(typetoken_latex)
    with open(ambiguity_path, 'w') as outfile:
        outfile.write(ambiguity_latex)


def compute_stats_includingpos(form_pos2prevalence_set, typetoken_headers, typetoken_path, ambiguity_headers, ambiguity_path, pos_set):
    """
    Compute descriptive statistics for a resource,
    for all POS together and for each POS separately,
    convert to LaTeX tables and save to .txt files.

    :param dict form_pos2prevalence_set: (form, POS) -> prevalence set
    :param list typetoken_headers: ['Type header', 'Token header']
    :param str typetoken_path: path to save the typetoken statistics to
    :param list ambiguity_headers: ['Ambiguity class', 'Frequency']
    :param str ambiguity_path: path to save the ambiguity statistics to
    :param set pos_set: all encountered POS in the resource

    :rtype: NoneType
    :return: None, the statistics are written to .txt files as LaTeX tables
    """
    # statistics for all POS together
    compute_stats(form_pos2prevalence_set, typetoken_headers, typetoken_path, ambiguity_headers, ambiguity_path, pos=pos_set)

    # statistics for each POS separately
    for pos in pos_set:
        typetoken_path_pos = f'{typetoken_path[:-4]}_{pos}.txt'
        ambiguity_path_pos = f'{ambiguity_path[:-4]}_{pos}.txt'
        compute_stats(form_pos2prevalence_set, typetoken_headers, typetoken_path_pos, ambiguity_headers, ambiguity_path_pos, pos={pos})
def flatten_list_tuples(lst):
    """
    Takes a list of tuples and flattens the tuples to return a list
    :param lst: A list containing of 1 dimensionsal tuples
    :return: list
    >>> flatten_list_tuples([(1, 2), (3, 4)])
    [1, 2, 3, 4]
    """
    return [y for x in lst for y in x]

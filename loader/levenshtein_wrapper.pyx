from libc.stdlib cimport malloc, free

cdef extern from "levenshtein.c":
    int levenshtein(char * a, char * b, unsigned int * column)

cpdef int lev_distance(str a, str b):
    """
    Wrapper for the function levenshtein who calculate the edit distance between
    two string a and b. It was defined to allow the execution of the C version of
    levenshtein in Cython code.
    If one string is empty, the function will return the length of the second one.
    If both strings are empty, the function will return 0.
    :param a: first string
    :type a: str
    :param b: second string
    :type b: str
    :return: the edit distance between a and b
    :rtype: int
    """
    if len(a) == 0 or len(b) == 0:
        return max(len(a), len(b))
    cdef bytes by_a = a.encode()
    cdef bytes by_b = b.encode()
    cdef char* ch_a = by_a
    cdef char* ch_b = by_b
    cdef unsigned int * column = <unsigned int *> malloc((len(a)+1) * sizeof(unsigned int))
    x = levenshtein(ch_a, ch_b, column)
    free(column)
    return x
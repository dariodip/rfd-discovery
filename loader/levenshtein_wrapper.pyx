from libc.stdlib cimport malloc, free

cdef extern from "levenshtein.c":
    int levenshtein(const char * a, const char * b, unsigned int * column)

cpdef int lev_distance(str a, str b):
    if len(a) == 0 or len(b) == 0:
        return 0
    cdef bytes by_a = a.encode()
    cdef bytes by_b = b.encode()
    cdef char* ch_a = by_a
    cdef char* ch_b = by_b
    cdef int max_size = max(len(a), len(b)) + 1
    cdef unsigned int * column = <unsigned int *> malloc(max_size * sizeof(unsigned int))
    x = levenshtein(ch_a, ch_b, column)
    free(column)
    return x
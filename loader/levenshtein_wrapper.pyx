
cdef extern from "levenshtein.c":
    int levenshtein(char * a, char * b)

cpdef int lev_distance(str a, str b):
    if len(a) == 0 or len(b) == 0:
        return 0
    cdef bytes by_a = a.encode()
    cdef bytes by_b = b.encode()
    cdef char* ch_a = by_a
    cdef char* ch_b = by_b
    x = levenshtein(ch_a, ch_b)
    return x
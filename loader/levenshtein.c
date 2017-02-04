#include <stdio.h>
#include <string.h>

#define MIN3(a, b, c) ((a) < (b) ? ((a) < (c) ? (a) : (c)) : ((b) < (c) ? (b) : (c)))

int levenshtein(char *, char *);

int levenshtein(char *s1, char *s2) {
    unsigned int s1len, s2len, x, y, lastdiag, olddiag, total_dist;
    s1len = (unsigned int) strlen(s1);
    s2len = (unsigned int) strlen(s2);
    if (s1len == 0 || s2len == 0) {
        return 0;
    }
    unsigned int* column = malloc(s1len * sizeof(unsigned int));
    for (y = 1; y <= s1len; y++)
        column[y] = y;
    for (x = 1; x <= s2len; x++) {
        column[0] = x;
        for (y = 1, lastdiag = x-1; y <= s1len; y++) {
            olddiag = column[y];
            column[y] = MIN3(column[y] + 1, column[y-1] + 1, lastdiag + (s1[y-1] == s2[x-1] ? 0 : 1));
            lastdiag = olddiag;
        }
    }
    total_dist = column[s1len];
    free(column);
    return total_dist;
}
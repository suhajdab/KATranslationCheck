#!/usr/bin/env python3
import collections

class GeneratorCounter(object):
    """
    Utility class that provides zero-overhead counting for generators.
    At any point in time, len(...) of this class provides the number of
    items iterated so far

    Usage example:

        mycountinggen = CountingTee(mygen)
        myfunc(mycountinggen) # Same result as myfunc(mygen)
        print(len(mycountinggen))
    """
    def __init__(self, gen):
        self.gen = gen
        self.count = 0
        self.iter = self.gen.__iter__()

    def reiter(self, reset_count=False):
        """
        Attempts to restart iterating over the generator.
        This will work properly for lists, for example.

        Set reset_count to True to also reset the internal counter
        """
        if reset_count:
            self.count = 0
        self.iter = self.gen.__iter__()

    def __iter__(self):
        return self

    def __next__(self):
        result = next(self.iter)  # raises if no next value
        self.count += 1
        return result

    def __len__(self):
        return self.count


def majority_vote_all(arr, return_absolute=False):
    """
    Perform a majority selection on the value in an array.
    The values are required to be quantized, i.e. if no values are equal
    but only close together, this method won't work (try using a KDE-based method)
    This algorithm is fast and works for huge datasets, however,
    and is well suited, for example, for analyzing FFT outputs
    (as FFT generates quantized outputs).

    majority_vote_all() return a list [(v, f)] which is ordered
    by descending commonness (equally common values are not ordered).
    f is the fraction of the total size of arr.
    If return_absolute == True, f is an absolute frequency.

    arr maybe any array-like structure or generator.
    """
    c = collections.Counter()
    gc = GeneratorCounter(arr)
    c.update(gc)
    most_common = c.most_common()
    if return_absolute:
        return most_common
    return [(rec[0], rec[1] / len(gc)) for rec in most_common]

def majority_vote(arr):
    """
    Wrapper for majority_vote_all() that only returns the most common value.
    The frequency of the value is ignored. None is returned if arr is empty.
    """
    mv = majority_vote_all(arr)
    return mv[0][0] if mv else None

#!/usr/bin/env python3
"""
Utility to print translated patterns for a language.
Requires IF pattern index to be built previous

./TranslatedPatterns.py -l sv-SE

Used to find out whether you have english translated patterns.
"""
import json
import os
import re
import operator

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="Commands")
    parser.add_argument('-l', '--language', default="de", help='The language directory to use/extract (e.g. de, es)')
    args = parser.parse_args()


    with open(os.path.join("transmap", args.language + ".ifpatterns.json")) as infile:
        ifpatterns = json.load(infile)

    input_re = re.compile(r"\[\[\s*☃\s*[a-z-]+\s*\d*\s*\]\]")

    noverlap = {}
    for pat in ifpatterns:
        engl = pat["english"]
        transl = pat["translated"]
        # Replace input tags by nothing
        engl = input_re.sub("", engl)
        transl_orig = transl
        transl = input_re.sub("", transl)
        # Find list of words, ignore non-word strings
        engl_words = set([w for w in engl.split() if w.isalpha()])
        transl_words = set([w for w in transl.split() if w.isalpha()])
        # Compute overlap
        overlap_size = len(engl_words.intersection(transl_words))
        if len(transl_words) > 0 and overlap_size > 0:
            noverlap[transl_orig] = overlap_size / len(transl_words)
    # Print in ascending severity
    for k,v in sorted(noverlap.items(), key=operator.itemgetter(1)):
        print(v, ";", k)

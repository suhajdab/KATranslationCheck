#!/usr/bin/env python3
"""
Utility to print translated patterns for a language.
Requires IF pattern index to be built previous

./TranslatedPatterns.py -l sv-SE

Used to find out whether you have english translated patterns.
"""
import json
import os

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="Commands")
    parser.add_argument('-l', '--language', default="de", help='The language directory to use/extract (e.g. de, es)')
    args = parser.parse_args()


    with open(os.path.join("transmap", args.language + ".ifpatterns.json")) as infile:
        ifpatterns = json.load(infile)

    for pat in map(lambda p: p["translated"], ifpatterns):
        print(pat.strip())

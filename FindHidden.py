#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import polib


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('tag', help='The tag to filter for (tcomment)')
    parser.add_argument('potfile', help='The POT file to read')
    parser.add_argument('n', type=int, help='How many words to look for')
    args = parser.parse_args()

    pot = polib.pofile(args.potfile)

    for po in pot:
        if args.tag not in po.tcomment:
            continue
        n = len(po.msgstr.split())
        if n == args.n:
            print("=================================")
            print(po.msgstr)
            print("=================================\n\n")
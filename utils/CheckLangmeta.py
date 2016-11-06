#!/usr/bin/env python3
"""
Check if language-meta.json contains all languages that are listed in the auto-generated languages.json
"""
import json

with open("../cache/languages.json") as infile:
    langs = json.load(infile)
with open("../language-meta.json") as infile:
    lmeta = json.load(infile)

lk1 = set(langs.keys())
lk2 = set(lmeta.keys())

print("Languages in Crowdin but not in languages-meta.json:")
print(lk1.difference(lk2))
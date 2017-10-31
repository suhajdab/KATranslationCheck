#!/usr/bin/env python3
import re
import json
import os

def get_text_regex():
    exceptions = ["cm", "m", "g", "kg", "s", "min", "max", "h", "cm"]
    exc_clause = "".join([r"(?! ?" + ex + r"\})" for ex in exceptions])
    regex = r"(\\(text|mathrm)\s*\{" + exc_clause + r")"
    return re.compile(regex)


def get_text_content_regex():
    return re.compile(r"(\\text\s*\{\s*)([^\}]+?)(\s*\})") 

def transmap_filename(lang, identifier):
    return os.path.join("transmap", "{}.{}.json".format(lang, identifier))

def read_patterns(lang, identifier):
    with open(transmap_filename(lang, identifier)) as infile:
        return json.load(infile)
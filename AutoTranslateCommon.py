#!/usr/bin/env python3
import re
import json
import os
from bs4 import BeautifulSoup

def get_text_regex():
    exceptions = ["cm", "m", "g", "kg", "s", "min", "max", "h", "cm"]
    exc_clause = "".join([r"(?! ?" + ex + r"\})" for ex in exceptions])
    regex = r"(\\(text|mathrm)\s*\{" + exc_clause + r")"
    return re.compile(regex)


def get_text_content_regex():
    return re.compile(r"(\\text\s*\{\s*)([^\}]+?)(\s*\})") 

def transmap_filename(lang, identifier, extension="json"):
    return os.path.join("transmap", "{}.{}.{}".format(
        lang, identifier, extension))

def read_patterns(lang, identifier):
    with open(transmap_filename(lang, identifier)) as infile:
        return json.load(infile)

def read_ifpattern_index(lang):
    try:
        ifpatterns = read_patterns(lang, "ifpatterns")
        return {
            v["english"]: v["translated"]
            for v in ifpatterns
            if v["translated"] # Ignore empty string == untranslated
            and v["english"].count("$formula$") == v["translated"].count("$formula$")
        }
    except FileNotFoundError:
        return {}

def read_texttag_index(lang):
    try:
        texttags = read_patterns(lang, "texttags")
        return {
            v["english"]: v["translated"]
            for v in texttags
            if v["translated"] # Ignore empty string == untranslated
        }
    except FileNotFoundError:
        return {}

def pattern_list_to_xliff(patterns):
    """
    Convert a JSON list to a XLIFF soup
    """
    # Read template XLIFF
    with open("template.xliff") as infile:
        soup = BeautifulSoup(infile, "lxml-xml")
    body = soup.xliff.file.body
    
    for pattern in patterns:
        trans = soup.new_tag("trans-unit")
        # Source
        source = soup.new_tag("source")
        source.append(pattern["english"])
        # Target
        target = soup.new_tag("target")
        target.append(pattern["translated"] if pattern["translated"] else pattern["english"])
        target.attrs["state"] = "needs-translations" \
            if pattern["translated"] == "" else "translated"
        # Assembly
        trans.append(source)
        trans.append(target)
        body.append(trans)
    return soup
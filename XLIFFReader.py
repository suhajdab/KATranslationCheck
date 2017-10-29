#!/usr/bin/env python3
from bs4 import BeautifulSoup
from AutoTranslationIndexer import *
import os.path

def parse_xliff_file(filename):
    with open(filename) as infile:
        return BeautifulSoup(infile, "lxml-xml")

def export_xliff_file(soup, filename):
    with open(filename, "w") as outfile:
        outfile.write(unicode(soup))

def process_xliff_soup(soup, translator, indexer):
    """
    Remove both untranslated and notes from the given soup.
    For the untranslated elements, in
    """
    body = soup.xliff.file.body
    for trans_unit in body.find_all("trans-unit"):
        source = trans_unit.source
        target = trans_unit.target
        note = trans_unit.note
        is_untranslated = (target["state"] == "needs-translation")

        engl = source.text
        translated = target.text
        # Index tags in the indexer (e.g. to extract text tags)
        # This is done even if they are translated
        indexer.add(engl, None if is_untranslated else translated)

        # Remove entire tag if translated (or suggested)
        if not is_untranslated:
            trans_unit.extract()
            continue

        # Remove HUGE note text to save space
        if note:
            note.extract()

if __name__ == "__main__":
    lang = "de"
    text_tag_indexer = TextTagIndexer()
    pattern_indexer = TextTagIndexer()
    indexer = CompositeIndexer(text_tag_indexer, pattern_indexer)

    soup = parse_xliff_file("cache/lol/2_high_priority_content/learn.math.precalculus.exercises.xliff")
    process_xliff_soup(soup, None, indexer)
    # Export indexed
    text_tag_indexer.exportCSV(os.path.join("output-" + lang, "texttags.csv"))
    pattern_indexer.exportCSV(os.path.join("output-" + lang, "patterns.csv"))

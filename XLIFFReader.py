#!/usr/bin/env python3
from bs4 import BeautifulSoup

def parse_xliff_file(filename):
    with open(filename) as infile:
        return BeautifulSoup(infile, "lxml-xml")

def export_xliff_file(soup, filename):
    with open(filename, "w") as outfile:
        outfile.write(unicode(soup))

def cleanup(soup):
    """
    Remove both untranslated and notes from the given soup
    """
    body = soup.xliff.file.body
    for trans_unit in body.find_all("trans-unit"):
        source = trans_unit.source
        target = trans_unit.target
        note = trans_unit.note
        is_untranslated = (target["state"] == "needs-translation")

        # Remove entire tag if translated (or suggested)
        if not is_untranslated:
            trans_unit.extract()
            continue # No need to remove 

        # Remove HUGE note text to save space
        if note:
            note.extract()

if __name__ == "__main__":
    soup = parse_xliff_file("cache/lol/2_high_priority_content/learn.math.precalculus.exercises.xliff")
    cleanup(soup)
    print(soup.prettify())

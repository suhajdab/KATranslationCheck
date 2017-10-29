#!/usr/bin/env python3
from bs4 import BeautifulSoup
from AutoTranslationIndexer import *
from AutoTranslationTranslator import *
import os.path
import os
from ansicolor import black
from UpdateAllFiles import *
from XLIFFUpload import *

def findXLIFFFiles(directory):
    """
    Get a list of PO files (.po / .pot) which are present in the directory.
    """
    transFilemap = getTranslationFilemapCache()
    if os.path.isfile(directory): #Single file>=
        poFilenames = [directory]
    else:
        poFilenames = {}
        #Recursively iterate directory, ignore everythin except *.po
        for (curdir, _, files) in os.walk(directory):
            for f in files:
                #Ignore non-PO files
                if not f.endswith(".xliff"): continue
                #Add to list of files to process
                filename = os.path.join(curdir, f)
                basename = os.path.basename(filename)
                poFilenames[filename] = transFilemap[basename.replace(".xliff", ".pot")]["id"]
    return poFilenames

def parse_xliff_file(filename):
    with open(filename) as infile:
        return BeautifulSoup(infile, "lxml-xml")

def export_xliff_file(soup, filename):
    with open(filename, "w") as outfile:
        outfile.write(str(soup))

def process_xliff_soup(filename, soup, autotranslator, indexer):
    """
    Remove both untranslated and notes from the given soup.
    For the untranslated elements, in
    """
    overall_count = 0
    untranslated_count = 0
    translated_count = 0
    autotranslated_count = 0
    # Iterate over all translatable strings
    body = soup.xliff.file.body
    for trans_unit in body.find_all("trans-unit"):
        overall_count += 1
        source = trans_unit.source
        target = trans_unit.target
        note = trans_unit.note
        is_untranslated = ("state" in target.attrs and target["state"] == "needs-translation")

        engl = source.text
        translated = target.text
        # Index tags in the indexer (e.g. to extract text tags)
        # This is done even if they are translated
        indexer.add(engl, None if is_untranslated else translated)

        # Remove entire tag if translated (or suggested)
        if not is_untranslated:
            trans_unit.extract()
            translated_count += 1
            continue  # Dont try to autotranslate etc

        untranslated_count += 1
        # Remove HUGE note text to save space
        if note:
            note.extract()
        # Remove empty text inside the <trans-unit> element to save space
        [c.extract() for c in trans_unit.contents]

        # Now we can try to autotranslate
        autotrans = autotranslator.translate(engl)
        if autotrans is None:  # Could not translate
            # Remove from output file to conserve space
            trans_unit.extract()
        else:  # Could autotranslate
            # Store autotranslation in XML
            target["state"] = "translated"
            target.string = autotrans
            autotranslated_count += 1

    # Remove empty text content of the body to conserve spce
    # TODO

    # Print stats
    print(black("Autotranslated {} of {} untranslated strings ({} total)".format(
        autotranslated_count, untranslated_count, overall_count), bold=True))

def readAndProcessXLIFF(lang, filename, indexer, autotranslator):
    soup = parse_xliff_file(filename)
    process_xliff_soup(filename, soup, autotranslator, indexer)
    # Export XLIFF
    outdir = "output-{}".format(lang)
    outfilename = filename.replace("cache/{}".format(lang), outdir)
    # Create directories
    os.makedirs(os.path.dirname(outfilename), exist_ok=True)
    print(black("Exporting to {}".format(outfilename), bold=True))
    export_xliff_file(soup, outfilename)
    # Return for possible auto upload etc
    return soup

def autotranslate_xliffs(args):
    os.makedirs("output-{}".format(args.language), exist_ok=True)

    # Initialize pattern indexers
    text_tag_indexer = TextTagIndexer()
    pattern_indexer = TextTagIndexer()
    indexer = CompositeIndexer(text_tag_indexer, pattern_indexer)

    # Initialize autotranslators
    rule_autotranslator = RuleAutotranslator()
    autotranslator = CompositeAutoTranslator(rule_autotranslator)

    xliffs = findXLIFFFiles("cache/{}".format(args.language))
    for filepath, fileid in xliffs.items():
        readAndProcessXLIFF(args.language, filepath, indexer, autotranslator)

    # Export indexed
    text_tag_indexer.exportCSV(os.path.join("output-" + args.language, "texttags.csv"))
    pattern_indexer.exportCSV(os.path.join("output-" + args.language, "patterns.csv"))

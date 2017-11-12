#!/usr/bin/env python3
from AutoTranslationIndexer import *
from AutoTranslationTranslator import *
import os.path
import os
import sys
from tqdm import tqdm
from ansicolor import black, blue, green
from UpdateAllFiles import *
from XLIFFUpload import *
import concurrent.futures
import gc
import bs4

def findXLIFFFiles(directory, filt=[]):
    """
    Get a list of PO files (.po / .pot) which are present in the directory.

    filter is a nested list from argparse which defined
    """
    transFilemap = getTranslationFilemapCache()
    if os.path.isfile(directory): #Single file>=
        poFilenames = [directory]
    else:
        xliffFiles = {} # name => crowdin file id
        #Recursively iterate directory, ignore everythin except *.po
        for (curdir, _, files) in os.walk(directory):
            # Ignore non-XLIFF files
            for f in filter(lambda f: f.endswith(".xliff"), files):
                #Add to list of files to process
                filename = os.path.join(curdir, f)
                basename = os.path.basename(filename)
                # Filter based on custom filter
                filtered = False # true => ignore this file
                # Ignore files not in filter, if any
                for subfilt1 in (filt or []):
                    for subfilt2 in subfilt1: # argparse creates nested list
                        if subfilt2 not in filename and subfilt2 not in filename.replace(".xliff", ".pot"):
                            filtered = True
                if not filtered: # passed filter
                    xliffFiles[filename] = transFilemap[basename.replace(".xliff", ".pot")]["id"]
    return xliffFiles

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
        # Broken XLIFF?
        if target is None:
            print(trans_unit.prettify())
            continue
        note = trans_unit.note
        is_untranslated = ("state" in target.attrs and target["state"] == "needs-translation")

        engl = source.text
        translated = target.text
        # Index tags in the indexer (e.g. to extract text tags)
        # This is done even if they are translated
        indexer.add(engl, None if is_untranslated else translated, filename=filename)

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
    tags = [elem.extract() for elem in body.children if isinstance(elem, bs4.element.Tag)]
    body.contents = tags

    # Print stats
    print(black("Autotranslated {} of {} untranslated strings ({} total) in {}".format(
        autotranslated_count, untranslated_count, overall_count, os.path.basename(filename))))

    return autotranslated_count

def readAndProcessXLIFF(lang, filename, fileid, indexer, autotranslator, upload=False, approve=False):
    soup = parse_xliff_file(filename)
    autotranslated_count = process_xliff_soup(filename, soup, autotranslator, indexer)
    # Export XLIFF
    outdir = "output-{}".format(lang)
    outfilename = filename.replace("cache/{}".format(lang), outdir)
    # Create directories & export
    if autotranslated_count > 0:
        os.makedirs(os.path.dirname(outfilename), exist_ok=True)
        #print(black("Exporting to {}".format(outfilename), bold=True))
        export_xliff_file(soup, outfilename)
    # Upload if enabled
    if upload and autotranslated_count > 0:
            basename = os.path.basename(filename)
            print(blue("Uploading {} (approve={})...".format(basename, approve)))
            upload_file(outfilename, fileid, auto_approve=approve, lang=lang)
            print(green("Uploaded {}".format(basename)))
    return autotranslated_count


def readAndProcessXLIFFRunner(*args, **kwargs):
    result = 0
    try:
        result = readAndProcessXLIFF(*args, **kwargs)
    except:
        print(sys.exc_info())
    gc.collect()
    return result


def autotranslate_xliffs(args):
    os.makedirs("output-{}".format(args.language), exist_ok=True)

    ignore_alltranslated = args.index_ignore_translated

    # Initialize pattern indexers
    text_tag_indexer = TextTagIndexer(args.language) if args.index else None
    pattern_indexer = GenericPatternIndexer() if args.index else None
    ignore_formula_pattern_idxer = IgnoreFormulaPatternIndexer(args.language) if args.index else None
    indexer = CompositeIndexer(text_tag_indexer, pattern_indexer, ignore_formula_pattern_idxer)

    # Initialize autotranslators
    rule_autotranslator = RuleAutotranslator()
    full_autotranslator = FullAutoTranslator(args.language) if args.full_auto else None
    ifpattern_autotranslator = IFPatternAutotranslator(args.language) if args.patterns else None
    name_autotranslator = NameAutotranslator(args.language) if args.name_autotranslate else None
    autotranslator = CompositeAutoTranslator(rule_autotranslator,
        full_autotranslator, name_autotranslator, ifpattern_autotranslator)

    # Process in parallel
    # Cant use process pool as indexers currently cant be merged
    executor = concurrent.futures.ThreadPoolExecutor(args.num_processes)

    xliffs = findXLIFFFiles("cache/{}".format(args.language), filt=args.filter)
    # Run XLIFF parser in 
    futures = [
        executor.submit(readAndProcessXLIFFRunner, args.language, filepath, fileid, indexer, autotranslator, upload=args.upload, approve=args.approve)
        for filepath, fileid in xliffs.items()
    ]
    # stats
    kwargs = {
        'total': len(futures),
        'unit': 'it',
        'unit_scale': True,
        'leave': True
    }
    autotranslated_count = 0
    for future in tqdm(concurrent.futures.as_completed(futures), **kwargs):
        autotranslated_count += future.result()

    print("\nAuto-translated {} strings !\n".format(autotranslated_count))

    # Export indexed
    if args.index:
        print("Exporting indices...")
        text_tag_indexer.exportJSON(ignore_alltranslated)
        text_tag_indexer.exportXLIFF(ignore_alltranslated)
        text_tag_indexer.exportXLSX(ignore_alltranslated)
        ignore_formula_pattern_idxer.exportJSON(ignore_alltranslated)
        ignore_formula_pattern_idxer.exportXLSX(ignore_alltranslated)
        ignore_formula_pattern_idxer.exportXLIFF(ignore_alltranslated)
        pattern_indexer.exportCSV(os.path.join("output-" + args.language, "patterns.csv"))

    if args.update_index_source:
        update_crowdin_index_files(args.language)

    if args.update_index:
        pass
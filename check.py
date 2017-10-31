#!/usr/bin/env python3
# coding: utf-8
"""
EXPERIMENTAL

Regular expression rule checker for Khan Academy translations.

Instructions:
 - Download https://crowdin.com/download/project/khanacademy.zip
 - Unzip the 'de' folder.
 - From the directory where the 'de' folder is located, run this script.
"""
import re
import operator
import simplejson as json
import itertools
import os
import os.path
import glob
import urllib
import shutil
import datetime
import functools
import concurrent.futures
import collections
from XLIFFReader import *
from toolz.dicttoolz import valfilter, merge, merge_with, keyfilter, valmap
from toolz.itertoolz import groupby, reduceby
from multiprocessing import Pool
from ansicolor import red, black, blue
from UpdateAllFiles import get_translation_urls
from Rules import Severity, importRulesForLanguage
from LintReport import readAndMapLintEntries, NoResultException

XLIFFEntry = collections.namedtuple("XLIFFEntry", ["english", "translated", "is_untranslated", "note"])

def writeToFile(filename, s):
    "Utility function to write a string to a file identified by its filename"
    with open(filename, "w") as outfile:
        outfile.write(s)

def writeJSONToFile(filename, obj):
    "Utility function to write a string to a file identified by its filename"
    with open(filename, "w") as outfile:
        json.dump(obj, outfile)

def findPOFiles(directory):
    """
    Get a list of PO files (.po / .pot) which are present in the directory.
    """
    if os.path.isfile(directory): #Single file>=
        poFilenames = [directory]
    else:
        poFilenames = []
        #Recursively iterate directory, ignore everythin except *.po
        for (curdir, _, files) in os.walk(directory):
            for f in files:
                #Ignore non-PO files
                if not f.endswith(".po") and not f.endswith(".pot"): continue
                #Add to list of files to process
                poFilenames.append(os.path.join(curdir, f))
    return poFilenames

_multiSpace = re.compile(r"\s+")

def genCrowdinSearchString(entry):
    s = entry.translated[:100].replace('*', ' ')
    s = s.replace('$', ' ').replace('\\', ' ').replace(',', ' ')
    s = s.replace('.', ' ').replace('?', ' ').replace('!', ' ')
    s = s.replace("-", " ").replace(":", " ")
    #Remove consecutive spaces
    s = _multiSpace.sub(" ", s)
    return urllib.parse.quote(s.replace('☃', ' ').replace("|", " "))

class JSONHitRenderer(object):
    """
    A state container for the code which applies rules and generates HTML.
    """
    def __init__(self, outdir, lang="de", num_processes=2):
        self.lang = lang
        # Create output directory
        self.outdir = os.path.join(outdir, lang)
        os.makedirs(self.outdir, exist_ok=True)
        # Async executor
        self.executor = concurrent.futures.ThreadPoolExecutor(num_processes)
        # Load rules for language
        rules, rule_errors = importRulesForLanguage(lang)
        self.rules = sorted(rules, reverse=True)
        self.rule_errors = rule_errors
        # Get timestamp
        self.timestamp = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
        # Process lastdownload date (copied to the templated)
        lastdownloadPath = os.path.join("cache", "lastdownload-{}.txt".format(lang))
        if os.path.isfile(lastdownloadPath):
            with open(lastdownloadPath) as infile:
                self.downloadTimestamp = infile.read().strip()
        else:
            self.downloadTimestamp = None
        # Initialize translation ID/URL map
        self.translationURLs = get_translation_urls(lang)

    def file_relpath(self, filename):
        return os.path.relpath(filename, os.path.join("cache", self.lang))

    def computeRuleHits(self, filename):
        """
        Compute all rule hits for a single parsed PO file and return a list of hits
        """
        # Compute relative path (which is how Crowin refers to the file)
        relpath = self.file_relpath(filename)
        # Read XLIFF
        basename = os.path.basename(filename)
        soup = parse_xliff_file(filename)
        try:
            body = soup.xliff.file.body
        except AttributeError:
            print(red("File {} is not valid XLIFF - Ignoring.".format(relpath)))
            return []
        # Iterate over all translatable strings and apply rule
        rule_hits = defaultdict(list)
        print(filename)
        for trans_unit in body.find_all("trans-unit"):
            # Extract info
            source = trans_unit.source
            target = trans_unit.target
            # Broken XLIFF entry
            if source is None or target is None:
                continue
            # Convert to XLIFF entry
            is_untranslated = ("state" in target.attrs and target["state"] == "needs-translation")
            entry = XLIFFEntry(source.text, target.text, is_untranslated, trans_unit.note.text)
            # Apply to rules
            for rule in self.rules:
                rule_hits[rule] += list(rule.apply_to_xliff_entry(entry, relpath))
        # Convert to list which is easier to process down the chain
        gc.collect()
        return [
            (relpath, rule, hits)
            for rule, hits in rule_hits.items()
        ]

    def computeRuleHitsForFileSet(self, xliffs):
        """
        For each file in the given filename -> PO object dictionary,
        compute the Rule -> Hits dictonary.

        Stores the information in the current instance.
        Does not return anything
        """
        # Compute dict with sorted & prettified filenames
        self.files = sorted(xliffs.keys())
        # Add all futures to the executor
        futures = [self.executor.submit(self.computeRuleHits, filename)
            for filename in xliffs.keys()]
        # Process the results in first-received order. Also keep track of rule performance
        self.fileRuleHits = collections.defaultdict(dict)
        n_finished = 0
        # Intermediate result storage
        raw_results = collections.defaultdict(dict) # filename -> {rule: result}
        for future in concurrent.futures.as_completed(futures):
            # Extract result
            for filename, rule, result in future.result():
                self.fileRuleHits[filename][rule] = result
            # Track progress
            n_finished += 1
            if n_finished % 1000 == 0:
                percent_finished = n_finished * 100. / len(futures)
                print("Rule computation finished {0:.2f} %".format(percent_finished))

        # Compute total stats by file
        self.statsByFile = {
            filename: merge(self.ruleHitsToSeverityCountMap(ruleHits), {
                            "translation_url": self.translationURLs[filename]})
            for filename, ruleHits in self.fileRuleHits.items()
        }
        # Compute map filename -> {rule: numHits for rule}
        self.statsByFileAndRule = {
            filename: valmap(len, ruleHits)
            for filename, ruleHits in self.fileRuleHits.items()
        }
        # Compute map rule -> numHits for rule
        self.totalStatsByRule = merge_with(sum, *(self.statsByFileAndRule.values()))

    def ruleHitsToSeverityCountMap(self, rule_hit_map):
        """
        In a rule -> hitlist mapping, count the total number of hits above or at a given severity
        level and return a cumulative dictionary
        """
        # Create a map severity -> count
        severity_counts = collections.defaultdict(int)
        for rule, hits in rule_hit_map.items():
            severity_counts[rule.severity] += len(hits)
        # Create string severity -> count map
        above_severity = lambda sev: sum(keyfilter(lambda k: k >= sev, severity_counts).values())
        return {"hits": above_severity(Severity.standard),
                "warnings": above_severity(Severity.warning),
                "errors": above_severity(Severity.dangerous),
                "infos": above_severity(Severity.info),
                "notices": above_severity(Severity.notice)}

    def countRuleHitsAboveSeverity(self, ruleHits, severity):
        return sum((len(hits) for rule, hits in ruleHits.items() if rule.severity >= severity))

    def writeStatsJSON(self):
        """
        Write a statistics-by-filename JSON to outdir/filestats.sjon
        """
        # Write file
        stats = {
            filename: {"hits": self.countRuleHitsAboveSeverity(ruleHits, Severity.standard),
                       "warnings": self.countRuleHitsAboveSeverity(ruleHits, Severity.warning),
                       "errors": self.countRuleHitsAboveSeverity(ruleHits, Severity.dangerous),
                       "infos": self.countRuleHitsAboveSeverity(ruleHits, Severity.info),
                       "notices": self.countRuleHitsAboveSeverity(ruleHits, Severity.notice)}
            for filename, ruleHits in self.fileRuleHits.items()
        }
        writeJSONToFile(os.path.join(self.outdir, "filestats.json"), stats)

    def _renderDirectory(self, ruleHits, ruleStats, directory, filename):
        # Generate output HTML for each rule
        for rule, hits in ruleHits.items():
            # Render hits for individual rule
            outfilePathJSON = os.path.join(directory, rule.machine_name + ".json")
            if len(hits) > 0:  # Render hits
                # Generate JSON API
                jsonAPI = {
                    "timestamp": self.timestamp,
                    "downloadTimestamp": self.downloadTimestamp,
                    "rule": rule.meta_dict,
                    # valfilter: remove empty values for smaller JSON
                    "hits": [valfilter(bool, {"msgstr": entry.translated,
                                              "msgid": entry.english,
                                              "tcomment": entry.note,
                                              "hit": hit,
                                              "origImages": origImages,
                                              "translatedImages": translatedImages,
                                              "crowdinLink": "{0}#q={1}".format(self.translationURLs[filename], genCrowdinSearchString(entry))
                                              })
                             for entry, hit, filename, origImages, translatedImages in hits]
                }
                writeJSONToFile(outfilePathJSON, jsonAPI)
            else:  # Remove file (redirects to 404 file) if there are no exportHitsAsJSON
                if os.path.isfile(outfilePathJSON):
                    os.remove(outfilePathJSON)
        # Render file index page (no filelist)
        ruleInfos = [merge(rule.meta_dict, {"num_hits": ruleStats[rule]})
                     for rule in self.rules if ruleStats[rule] > 0]
        ruleInfos.sort(key=lambda o: -o["severity"])  # Invert sort order
        js = {
            "pageTimestamp": self.timestamp,
            "downloadTimestamp": self.downloadTimestamp,
            "stats": ruleInfos,
            "files": [merge(self.statsByFile[filename], {"filename": filename})
                      for filename in map(self.file_relpath, self.files)
                      if self.statsByFile[filename]["notices"] > 0]
        }
        writeJSONToFile(os.path.join(directory, "index.json"), js)

    def exportHitsAsJSON(self):
        """
        Apply a rule and write a directory of output HTML files
        """
        for filename, ruleHits in self.fileRuleHits.items():
            rule_stats = self.statsByFileAndRule[filename]
            # Ensure output directory is present
            directory = os.path.join(self.outdir, filename)
            os.makedirs(directory, exist_ok=True)
            # Perform rendering
            self._renderDirectory(ruleHits, rule_stats, directory, filename)
        #####################
        ## Render overview ##
        #####################
        # Compute global hits for every rule
        overview_hits = {
            rule: list(itertools.chain(*(fileHits[rule] for fileHits in self.fileRuleHits.values())))
            for rule in self.rules
        }
        self._renderDirectory(overview_hits, self.totalStatsByRule, self.outdir, filename="All files")
        # Create rule error file
        writeJSONToFile(os.path.join(self.outdir, "ruleerrors.json"),
                        [err.msg for err in self.rule_errors])
        # Copy static files
        for filename in glob.glob("templates/*"):
            shutil.copyfile(filename, os.path.join(self.outdir, os.path.split(filename)[-1]))

def renderLint(outdir, kalangcode):
    "Parse & render lint"
    # Map from KA code to crowdin code
    langMap = {"pt": "pt-BR", "pt-pt": "pt-PT", "ur": "ur-PK", "es": "es-ES", "hy": "hy-AM"}
    lang = langMap[kalangcode] if kalangcode in langMap else kalangcode
    print(black("Rendering lint for {0} ({1})".format(lang, kalangcode), bold=True))
    # Generate lint report
    lintFilename = os.path.join("cache", "{0}-lint.csv".format(kalangcode))
    if os.path.isfile(lintFilename):
        lintEntries = list(readAndMapLintEntries(lintFilename, lang))
        # Write JSON
        jsonEntries = list(map(operator.methodcaller("_asdict"), lintEntries))
        os.makedirs(os.path.join(outdir, lang), exist_ok=True)
        writeJSONToFile(os.path.join(outdir, lang, "lint.json"), jsonEntries)
    else:
        print("Skipping lint ({0} does not exist)".format(lintFilename))

def renderAllLints(outdir):
    rgx = re.compile(r"([a-z]{2}(-[a-z]{2})?)-lint.csv")
    for f in os.listdir("cache"):
        m = rgx.match(f)
        if m is None: continue
        lang = m.group(1)
        renderLint(outdir, lang)

def performRenderLint(args):
    renderAllLints("output")

def performRender(args):
    # Download / update if requested
    if args.download:
        download()

    # Create directory
    if not args.outdir:
        args.outdir = "output"
    os.makedirs(args.outdir, exist_ok=True)

    renderer = JSONHitRenderer(args.outdir, args.language, args.num_processes)

    # Import
    potDir = os.path.join("cache", args.language)
    xliffFiles = findXLIFFFiles(potDir, filt=args.filter)
    print(black("Reading {} files from {} folder...".format(len(xliffFiles), potDir), bold=True))
    # Compute hits
    print(black("Computing rules...", bold=True))
    renderer.computeRuleHitsForFileSet(xliffFiles)

    # Generate HTML
    print(black("Rendering HTML...", bold=True))
    renderer.exportHitsAsJSON()

    # Generate filestats.json
    print (black("Generating JSON API files...", bold=True))
    renderer.writeStatsJSON()

    # If data is present, generate subtitle information
    videosJSONPath = os.path.join("cache", "videos.json")
    if os.path.isfile(videosJSONPath):
        print (black("Rendering subtitles overview...", bold=True))
        with open(videosJSONPath) as infile:
            exercises = json.load(infile)
        subtitleTemplate = renderer.env.get_template("subtitles.html")
        writeToFile(os.path.join(args.outdir, "subtitles.html"), subtitleTemplate.render(exercises=exercises))

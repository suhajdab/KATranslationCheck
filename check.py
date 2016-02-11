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
import polib
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
from toolz.dicttoolz import valfilter, merge, merge_with, keyfilter, valmap
from toolz.itertoolz import groupby, reduceby
from multiprocessing import Pool
from ansicolor import red, black, blue
from UpdateAllFiles import getTranslationFilemapCache
from Rules import Severity, importRulesForLanguage
from LintReport import readAndMapLintEntries, NoResultException

def writeToFile(filename, s):
    "Utility function to write a string to a file identified by its filename"
    with open(filename, "w") as outfile:
        outfile.write(s)

def writeJSONToFile(filename, obj):
    "Utility function to write a string to a file identified by its filename"
    with open(filename, "w") as outfile:
        json.dump(obj, outfile)

def readPOFiles(directory):
    """
    Read all PO files from a given directory and return
    a dictionary path -> PO object.

    Also supports using a single file as argument.
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
    # Parsing is computationally expensive.
    # Distribute processing amongst distinct processing
    #  if there is a significant number of files
    if len(poFilenames) > 10:
        pool = Pool(None) #As many as CPUs
        parsedFiles = pool.map(polib.pofile, poFilenames)
        return {path: parsedFile
                   for path, parsedFile
                   in zip(poFilenames, parsedFiles)}
    else: #Only a small number of files, process directly
        return {path: polib.pofile(path) for path in poFilenames}

_multiSpace = re.compile(r"\s+")

def genCrowdinSearchString(entry):
    s = entry.msgstr[:100].replace('*', ' ')
    s = s.replace('$', ' ').replace('\\', ' ').replace(',', ' ')
    s = s.replace('.', ' ').replace('?', ' ').replace('!', ' ')
    s = s.replace("-", " ").replace(":", " ")
    #Remove consecutive spaces
    s = _multiSpace.sub(" ", s)
    return urllib.parse.quote(s.replace('☃', ' ').replace("|", " "))

class HTMLHitRenderer(object):
    """
    A state container for the code which applies rules and generates HTML.
    """
    def __init__(self, outdir, lang="de"):
        self.outdir = outdir
        self.lang = lang
        # Async executor
        self.executor = concurrent.futures.ThreadPoolExecutor(os.cpu_count())
        # Load rules for language
        rules, rule_errors = importRulesForLanguage(lang)
        self.rules = sorted(rules, reverse=True)
        self.rule_errors = rule_errors
        # Get timestamp
        self.timestamp = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
        #Process lastdownload date (copied to the templated)
        lastdownloadPath = os.path.join("cache", "lastdownload-{0}.txt".format(lang))
        if os.path.isfile(lastdownloadPath):
            with open(lastdownloadPath) as infile:
                self.downloadTimestamp = infile.read().strip()
        else:
            self.downloadTimestamp = None
        # Initialize translation ID/URL map
        translationFilemapCache = getTranslationFilemapCache()
        self.translationURLs = {
            "cache/{0}/{1}".format(lang, v["path"]):
                "https://crowdin.com/translate/khanacademy/{0}/enus-{1}".format(v["id"], lang)
            for v in translationFilemapCache.values()
        }
    def filepath_to_url(self, filename):
        return filename.replace("/", "_")
    def computeRuleHits(self, po, filename="[unknown filename]"):
        """
        Compute all rule hits for a single parsed PO file and return a list of futures
        that return (filename, rule, results tuples)
        """
        def _apply_wrapper(rule, po, filename):
            return (filename, rule, list(rule.apply_to_po(po, filename=filename)))
        futures = [self.executor.submit(_apply_wrapper, rule, po, filename) for rule in self.rules]
        return futures

    def computeRuleHitsForFileSet(self, poFiles):
        """
        For each file in the given filename -> PO object dictionary,
        compute the Rule -> Hits dictonary.

        Stores the information in the current instance.
        Does not return anything
        """
        # Compute dict with sorted & prettified filenames
        files = {filename: self.filepath_to_url(filename) for filename in poFiles.keys()}
        self.files = collections.OrderedDict(sorted(files.items()))
        # Add all futures to the executor
        futures = list(itertools.chain(*(self.computeRuleHits(po, filename)
                                         for filename, po in poFiles.items())))
        # Process the results in first-received order. Also keep track of rule performance
        self.fileRuleHits = collections.defaultdict(dict)
        n_finished = 0
        # Intermediate result storage
        raw_results = collections.defaultdict(dict) # filename -> {rule: result}
        for future in concurrent.futures.as_completed(futures):
            # Extract result
            filename, rule, result = future.result()
            self.fileRuleHits[filename][rule] = result
            # Track progress
            n_finished += 1
            if n_finished % 1000 == 0:
                percent_finished = n_finished * 100. / len(futures)
                print("Rule computation finished {0:.2f} %".format(percent_finished))

        # Compute total stats by file

        self.statsByFile = {
            filename: merge(self.ruleHitsToSeverityCountMap(ruleHits), {
                            "link": self.filepath_to_url(filename),
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
                       "notices": self.countRuleHitsAboveSeverity(ruleHits, Severity.notice),
                       "link": self.filepath_to_url(filename)}
            for filename, ruleHits in self.fileRuleHits.items()
        }
        writeJSONToFile(os.path.join(self.outdir, "filestats.json"), stats)
    def _renderDirectory(self, ruleHits, ruleStats, directory, filename, filelist={}):
        # Generate output HTML for each rule
        for rule, hits in ruleHits.items():
            # Render hits for individual rule
            outfilePathJSON = os.path.join(directory, rule.machine_name + ".json")
            if hits:  # Render hits
                # Generate JSON API
                jsonAPI = {
                    "timestamp": self.timestamp,
                    "downloadTimestamp": self.downloadTimestamp,
                    "rule": rule.meta_dict,
                    "hits": [valfilter(bool, {"msgstr": entry.msgstr, # valfilter: remove empty values for smaller JSON
                                              "msgid": entry.msgid,
                                              "tcomment": entry.tcomment,
                                              "hit": hit,
                                              "origImages": origImages,
                                              "translatedImages": translatedImages})
                             for entry, hit, filename, origImages, translatedImages in hits]
                }
                writeJSONToFile(outfilePathJSON, jsonAPI)
            else:  # Remove file (redirects to 404 file) if there are no hitsToHTML
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
        }
        if filelist:
            js["files"] = [
                merge(self.statsByFile[filename], {"filename": filename})
                for filename, filelink in filelist.items()
                if self.statsByFile[filename]["notices"]
            ]
        writeJSONToFile(os.path.join(directory, "index.json"), js)
    def hitsToHTML(self):
        """
        Apply a rule and write a directory of output HTML files
        """
        for filename, ruleHits in self.fileRuleHits.items():
            filepath = self.filepath_to_url(filename)
            ruleStats = self.statsByFileAndRule[filename]
            # Ensure output directory is present
            directory = os.path.join(self.outdir, filepath)
            if not os.path.isdir(directory):
                os.mkdir(directory)
            # Perform rendering
            self._renderDirectory(ruleHits, ruleStats, directory, filename, {})
        #####################
        ## Render overview ##
        #####################
        # Compute global hits for every rule
        overviewHits = {
            rule: itertools.chain(*(fileHits[rule] for fileHits in self.fileRuleHits.values()))
            for rule in self.rules
        }
        self._renderDirectory(overviewHits, self.totalStatsByRule, self.outdir, filename="all files", filelist=self.files)
        # Create rule error file
        writeJSONToFile(os.path.join(self.outdir, "ruleerrors.json"),
            [err.msg for err in self.rule_errors])
        # Copy static files
        for filename in glob.glob("templates/*"):
            shutil.copyfile(filename, os.path.join(self.outdir, os.path.split(filename)[-1]))

def renderLint(outdir, lang):
    "Parse & render lint"
    lintFilename = os.path.join("cache", "{0}-lint.csv".format(lang))
    if os.path.isfile(lintFilename):
        lintEntries = list(readAndMapLintEntries(lintFilename, lang))
        # Write JSON
        jsonEntries = list(map(operator.methodcaller("_asdict"), lintEntries))
        writeJSONToFile(os.path.join(outdir, "lint-{0}.json".format(lang)), jsonEntries)
    else:
        print("Skipping lint (%s does not exist)" % lintFilename)

def renderAllLints(outdir):
    rgx = re.compile(r"([a-z]{2}(-[a-z]{2})?)-lint.csv")
    for f in os.listdir("cache"):
        m = rgx.match(f)
        if m is None: continue
        lang = m.group(1)
        print(black("Rendering lint for {0}".format(lang), bold=True))
        renderLint(outdir, lang)

def performRenderLint(args):
    renderAllLints(args.outdir)

def performRender(args):
    # Download / update if requested
    if args.download:
        download()

    # Create directory
    if not args.outdir:
        args.outdir = "output-{0}".format(args.language)
    if not os.path.isdir(args.outdir):
        os.mkdir(args.outdir)

    renderer = HTMLHitRenderer(args.outdir, args.language)

    # Import
    potDir = os.path.join("cache", args.language)
    print(black("Reading files from {0} folder...".format(potDir), bold=True))
    poFiles = readPOFiles(potDir)
    print(black("Read {0} files".format(len(poFiles)), bold=True))
    # Compute hits
    print(black("Computing rules...", bold=True))
    renderer.computeRuleHitsForFileSet(poFiles)
    # Ensure the HUGE po stuff goes out of scope ASAP
    poFiles = None

    # Generate HTML
    print(black("Rendering HTML...", bold=True))
    renderer.hitsToHTML()

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

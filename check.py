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
import urllib
import shutil
import datetime
import collections
from toolz.dicttoolz import valfilter
from multiprocessing import Pool
from ansicolor import red, black, blue
from jinja2 import Environment, FileSystemLoader
from UpdateAllFiles import getTranslationFilemapCache
from Rules import Severity, importRulesForLanguage
from LintReport import readAndMapLintEntries, NoResultException
from compressinja.html import HtmlCompressor

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
        # Load rules for language
        rules, rule_errors = importRulesForLanguage(lang)
        self.rules = sorted(rules, reverse=True)
        self.rule_errors = rule_errors
        #Initialize template engine
        self.env = Environment(loader=FileSystemLoader('templates'), trim_blocks=True, lstrip_blocks=True, extensions=[HtmlCompressor])
        self.ruleTemplate = self.env.get_template("template.html")
        self.indexTemplate = self.env.get_template("index.html")
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
        Compute all rule hits for a single parsed PO file
        """
        unsorted = {
            rule: list(rule.apply_to_po(po, filename=filename))
            for rule in self.rules
        }
        return collections.OrderedDict(sorted(unsorted.items(), key=operator.itemgetter(0)))
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
        # Apply rules
        self.fileRuleHits = {
            filename: self.computeRuleHits(po, filename)
            for filename, po in poFiles.items()
        }
        # Compute total stats by file
        self.statsByFile = {
            filename: {"hits": self.countRuleHitsAboveSeverity(ruleHits, Severity.standard),
               "warnings": self.countRuleHitsAboveSeverity(ruleHits, Severity.warning),
               "errors": self.countRuleHitsAboveSeverity(ruleHits, Severity.dangerous),
               "infos": self.countRuleHitsAboveSeverity(ruleHits, Severity.info),
               "notices": self.countRuleHitsAboveSeverity(ruleHits, Severity.notice),
               "link": self.filepath_to_url(filename)}
            for filename, ruleHits in self.fileRuleHits.items()
        }
        # Compute by-rule stats per file
        self.statsByFileAndRule = {
            filename: {rule: len(hits) for rule, hits in ruleHits.items()}
            for filename, ruleHits in self.fileRuleHits.items()
        }
        # Compute total stats per rule
        self.totalStatsByRule = {
            rule: sum((stat[rule] for stat in self.statsByFileAndRule.values()))
            for rule in self.rules
        }
    def countRuleHitsAboveSeverity(self, ruleHits, severity):
        """In a rule -> hitlist mapping, count the total number of hits above a given severity"""
        return sum((len(hits) for rule, hits in ruleHits.items() if rule.severity >= severity))
    def countRuleHitsAtSeverity(self, ruleHits, severity):
        """In a rule -> hitlist mapping, count the total number of hits above a given severity"""
        return sum((len(hits) for rule, hits in ruleHits.items() if rule.severity == severity))
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
            outfilePath = os.path.join(directory, rule.get_machine_name() + ".html")
            outfilePathJSON = os.path.join(directory, rule.get_machine_name() + ".json")
            if hits:  # Render hits
                writeToFile(outfilePath,
                    self.ruleTemplate.render(hits=hits, timestamp=self.timestamp, downloadTimestamp=self.downloadTimestamp, translationURLs=self.translationURLs, urllib=urllib, rule=rule, genCrowdinSearchString=genCrowdinSearchString))
                # Generate JSON API
                jsonAPI = {
                    "timestamp": self.timestamp,
                    "downloadTimestamp": self.downloadTimestamp,
                    "hits": [valfilter(bool, {"msgstr": entry.msgstr,
                                              "msgid": entry.msgid,
                                              "tcomment": entry.tcomment,
                                              "origImages": origImages,
                                              "translatedImages": translatedImages})
                             for entry, hit, filename, origImages, translatedImages in hits]
                }
                writeJSONToFile(outfilePathJSON, jsonAPI)
            else:  # Remove file (redirects to 404 file) if there are no hitsToHTML
                if os.path.isfile(outfilePath):
                    os.remove(outfilePath)
                if os.path.isfile(outfilePath):
                    os.remove(outfilePath)
        # Render file index page (no filelist)
        writeToFile(os.path.join(directory, "index.html"),
            self.indexTemplate.render(rules=self.rules, timestamp=self.timestamp, files=filelist, statsByFile=self.statsByFile,
                          statsByRule=ruleStats, downloadTimestamp=self.downloadTimestamp, filename=filename, translationURLs=self.translationURLs))
        ruleInfos = [{
            "name": rule.name,
            "severity": rule.severity,
            "num_hits": ruleStats[rule],
            "color": rule.getBootstrapColor(),
            "machine_name": rule.get_machine_name()
        } for rule in self.rules if ruleStats[rule] > 0]
        ruleInfos.sort(key=lambda o: -o["severity"]) # Invert sort order
        js = {
            "pageTimestamp": self.timestamp,
            "downloadTimestamp": self.downloadTimestamp,
            "stats": ruleInfos
        }

        if filelist:
            js["files"] = {
                filename: self.statsByFile[filename],
                for filename, filelink in filelist.items()
                if self.statsByFile[filename]["notices"]
            }
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
        shutil.copyfile("templates/katc.js", os.path.join(self.outdir, "katc.js"))
        shutil.copyfile("templates/katc.css", os.path.join(self.outdir, "katc.css"))
        shutil.copyfile("templates/robots.txt", os.path.join(self.outdir, "robots.txt"))
        shutil.copyfile("templates/404.html", os.path.join(self.outdir, "404.html"))
        shutil.copyfile("templates/lint.ts", os.path.join(self.outdir, "lint.ts"))
        shutil.copyfile("templates/lint.html", os.path.join(self.outdir, "lint.html"))

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

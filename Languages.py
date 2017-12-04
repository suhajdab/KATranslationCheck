#!/usr/bin/env python3
import requests
import re
import json
import os.path
from ansicolor import black
from multiprocessing import Pool

def fetchLanguageID(lang):
    """
    Fetch the crowdin language ID
    """
    response = requests.get("https://crowdin.com/project/khanacademy/{0}".format(lang))
    match = re.search(r"CURRENT_LANGUAGE_ID\s*=\s*\"?(\d+)\"?", response.text)
    if match is None:
        #print(response.text)
        raise Exception("Cant find language ID for {}!".format(lang))
    return int(match.group(1))

def findAllLanguages():
    """
    Acquire a dictionary language -> lang ID from Crowdin
    """
    "Find a list of Crowdin language codes to which KA is translated to"
    # Acquire language list
    print(black("Fetching language list...", bold=True))
    response = requests.get("https://crowdin.com/project/khanacademy")
    txt = response.text
    langs = re.findall(r"https?://[a-z0-9]*\.cloudfront\.net/[0-9a-z]+/images/flags/([^\.]+)\.png", txt)
    print(black("Fetching language IDs...", bold=True))
    # English is the source language
    if "en-US" in langs:
        langs.remove("en-US")
    # Fetch lang IDs in parallel
    pool = Pool(32)
    return dict(zip(langs, pool.map(fetchLanguageID, langs)))

langsFile = "cache/languages.json"

def updateLangsFile():
    langs = findAllLanguages()
    with open(langsFile, "w") as outfile:
        json.dump(langs, outfile)

def getCachedLanguageMap():
    "Get the language map or download it if it is not present"
    if not os.path.isfile(langsFile):
        updateLangsFile()
    with open(langsFile, "r") as infile:
        return json.load(infile)

def findAvailableLanguages(directory="cache"):
    """
    Find available languages in the cache directory,
    i.e. subdirectories and return a {lang: absolute dirpath} map
    """
    ret = {}
    for child in os.listdir(directory):
        path = os.path.join(directory, child)
        if not os.path.isdir(path):
            continue
        ret[child] = path
    return ret

if __name__ == "__main__":
    print(findAllLanguages())
#!/usr/bin/env python3
import requests
import re
import json
import os.path

def findAllLanguages():
    "Find a list of Crowdin language codes to which KA is translated to"
    response = requests.get("https://crowdin.com/project/khanacademy")
    txt = response.text
    langs = {}
    for lang in re.findall(r"https?://[a-z0-9]*\.cloudfront\.net/images/flags/([^\.]+)\.png", txt):
        if lang == "en-US": continue
        print("Fetching language ID for {0}".format(lang))
        response = requests.get("https://crowdin.com/project/khanacademy/{0}/activity".format(lang))
        langid = int(re.search(r"GLOBAL_CURRENT_LANGUAGE_ID\s+=\s+(\d+)", response.text).group(1))
        langs[lang] = langid
    return langs

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

if __name__ == "__main__":
    print(findAllLanguages())
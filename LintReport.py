#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Official Khan Academy Lint reader
"""
from collections import namedtuple
import csv
import os
import requests
import time
import re
from ansicolor import black
from html.parser import HTMLParser
from UpdateAllFiles import downloadCrowdinById, getCrowdinSession
import shelve

LintEntry = namedtuple("LintEntry", ["date", "url", "crid", "text",
                                     "msgid", "msgstr", "comment", "filename"])

cache = None

def downloadCrowdinByIdCached(session, crid, lang):
    global cache
    cacheKey = "{0}-{1}".format(lang, crid)
    if cache is None:
        cache = shelve.open("/tmp/katc-cache")
    if cacheKey in cache:
        return cache[cacheKey]
    # TODO cache expiration
    cdata = downloadCrowdinById(session, crid, lang)
    cache[cacheKey] = cdata
    return cdata


class NoResultException(Exception):
    pass

def readLintCSV(filename):
    "Read a KA lint file"
    with open(filename) as lintin:
        reader = csv.reader(lintin, delimiter=',')
        return [LintEntry(row[0], row[1], row[1].rpartition("#")[2],
                row[2], None, None, None, None) for row in reader]


def readAndMapLintEntries(filename, lang="de"):
    """
    Enrich a list of lint entries with msgid and msgstr information
    """
    session = getCrowdinSession(domain="https://crowdin.com")
    cnt = 0
    h = HTMLParser()
    for entry in readLintCSV(filename):
        if entry.crid.startswith("https://translate.khanacademy.org"):
            msgid = "[KA Translate link]"
            msgstr = "[KA Translate link]"
            comment = "[KA Translate link]"
            filename = "[KA Translate link]"
        else:
            msgid, msgstr, comment, filename = downloadCrowdinByIdCached(session, entry.crid, lang)
        #comment = re.sub(__urlRegex, r"<a href=\"\1\">\1</a>", comment)
        msgid = msgid.replace(" ", "⸱").replace("\t", "→")
        msgstr = msgstr.replace(" ", "⸱").replace("\t", "→")
        comment = h.unescape(comment).replace("<a href=", "<a target=\"_blank\" href=")
        yield LintEntry(entry.date, entry.url,
                        entry.crid, entry.text, msgid, msgstr, comment, filename)
        cnt += 1
        if cnt % 100 == 0:
            print("Mapped {0} lint entries".format(cnt))


if __name__ == "__main__":
    url = getLatestLintPostURLForLanguage()
    print(url)
    #print(list(getMappedLintEntries("cache/de-lint.json")))
    #print(readLintCSV("de-lint.csv"))
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
    if cache is None:
        cache = shelve.open("/tmp/katc-cache")
    if crid in cache:
        return cache[crid]
    # TODO cache expiration
    cdata = downloadCrowdinById(session, crid, lang)
    cache[crid] = cdata
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
        msgid, msgstr, comment, filename = downloadCrowdinByIdCached(session, lang + "-" + entry.crid, lang)
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
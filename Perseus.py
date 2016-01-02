#!/usr/bin/env python3
import requests
import re

def getKAPerseusCommands():
    """Get a list of valid commands for KA Perseus"""
    txt = requests.get("https://github.com/Khan/perseus/raw/master/lib/katex/katex.js").text
    rgx = re.compile(r'"\\+([A-Za-z0-9]+)"')
    nonRGX = re.compile(r'u[0-9a-f]{4}')  # Skip unicode escapes, e.g. u25ca
    return list(filter(lambda s: s and not nonRGX.match(s), re.findall(rgx, txt)))

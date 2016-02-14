#!/usr/bin/env python3
import requests
import re
import os

def getKAPerseusCommands():
    """Get a list of valid commands for KA Perseus"""
    txt = requests.get("https://github.com/Khan/perseus/raw/master/lib/katex/katex.js").text
    rgx = re.compile(r'"\\+([A-Za-z0-9]+)"')
    nonRGX = re.compile(r'u[0-9a-f]{4}')  # Skip unicode escapes, e.g. u25ca
    return list(filter(lambda s: s and not nonRGX.match(s), re.findall(rgx, txt)))

def getCachedKAPerseusCommands():
    cachefile = os.path.join("cache", "perseus-commands.txt")
    if os.path.isfile(cachefile):
        with open(cachefile) as cachein:
            return [s.strip() for s in cachein.read().split("\n")]
    else:
        cmds = getKAPerseusCommands()
        with open(cachefile, "w") as cacheout:
            cacheout.write("\n".join(cmds))
        return cmds


if __name__ == "__main__":
    print(getCachedKAPerseusCommands())
#!/usr/bin/env python3
from bottle import route, run, request, response
import YakDB
import json
import os.path
from Languages import findAvailableLanguages

conn = YakDB.Connection()
conn.connect("tcp://localhost:7100")

# Load video map
with open(os.path.join("cache", "VideoMap.json")) as videofile:
    videomap = json.load(videofile)

@route('/translate.json')
def translateAPI():
    # Get english version from inex table
    key = conn.read(2, request.query.s)[0]
    # Get all language version
    result = conn.read(1, key)[0]
    # Split result into language/string pairs
    ret = {"en": key.decode("utf-8")}
    langvals = result.split(b"\x00")
    # Split language/strings and assemble JSON
    for langval in langvals:
        vallist = langval.split(b"\x1D")
        lang = vallist[0].decode("utf-8")
        string = vallist[1].decode("utf-8")
        ret[lang] = string
    return ret

@route('/videos.json')
def videoAPI():
    if request.query.id in videomap:
        return videomap[request.query.id]
    else:
        return {}

@route('/languages.json')
def langaugesAPI():
    response.content_type = 'application/json'
    return json.dumps(list(findAvailableLanguages().keys()) + ["en"])



run(host='localhost', port=7798, debug=True)
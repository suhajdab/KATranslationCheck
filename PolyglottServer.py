#!/usr/bin/env python3
from bottle import route, run, request
import YakDB

conn = YakDB.Connection()
conn.connect("tcp://localhost:7100")

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

run(host='localhost', port=8080, debug=True)
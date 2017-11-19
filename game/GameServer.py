#!/usr/bin/env python3
from bottle import run, request, response, Bottle
import simplejson as json
import random
import bs4
import dbm.dumb as dbm
from collections import namedtuple, Counter
from AutoTranslateCommon import transmap_filename
from XLIFFReader import parse_xliff_file

db = dbm.open("kagame.dbm", flag='c')

app = Bottle()

Translation = namedtuple("Translation", ["id", "source", "target"])

strings = None
fileid = None
targetlang = ""


def extract_strings_from_xliff_soup(filename, soup):
    """
    Remove both untranslated and notes from the given soup.
    For the untranslated elements, in
    """
    results = []

    global fileid
    global targetlang
    fileid = soup.xliff.file.attrs["id"]
    targetlang = soup.xliff.file.attrs["target-language"].partition("-")[0]

    for trans_unit in soup.xliff.file.body.children: #body.find_all("trans-unit"):
        # Ignore strings
        if not isinstance(trans_unit, bs4.element.Tag):
            continue

        # Ignore other tags
        if trans_unit.name != "trans-unit":
            print("Encountered wrong tag: {}".format(trans_unit.name))
            continue

        source = trans_unit.source
        target = trans_unit.target
        # Broken XLIFF?
        if target is None:
            print(trans_unit.prettify())
            continue
        note = trans_unit.note
        is_untranslated = ("state" in target.attrs and target["state"] == "needs-translation")
        is_approved = ("approved" in trans_unit.attrs and trans_unit["approved"] == "yes")
        strid = trans_unit["id"]

        engl = source.text
        translated = target.text

        # only suggested strings
        if not is_untranslated and not is_approved:
            results.append(Translation(strid, engl, translated))

    return results

@app.hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

@app.route('/api/strings')
def strings():
    choices = [random.choice(strings) for _ in range(10)]
    response.content_type = 'application/json'
    return json.dumps(choices)

@app.post('/api/submit')
def submit():
    cid = request.forms.get('client')
    string = request.forms.get('string')
    score = request.forms.get('score')
    db[string + ":" + cid] = score

@app.get('/api/db')
def submit():
    ctr = Counter()
    for sid, score in db.items():
        string, _, cid = sid.decode("utf-8").partition(":")
        ctr[int(string)] += int(score.decode("utf-8"))
    response.content_type = 'application/json'
    return json.dumps([{
        "url": "https://crowdin.com/translate/khanacademy/{}/enus-{}#{}".format(fileid, targetlang, strid),
        "id": strid,
        "score": cnt
    } for strid, cnt in ctr.most_common()])

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='The file to read')
    args = parser.parse_args()

    soup = parse_xliff_file(args.file)
    strings = extract_strings_from_xliff_soup(args.file, soup)
    run(app, host='localhost', port=9922)

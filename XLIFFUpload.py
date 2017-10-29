#!/usr/bin/env python3
import requests
import os.path
from UpdateAllFiles import getCrowdinSession

def upload_file(filename, fileid, auto_approve=False, lang="lol"):
    auto_approve = 1 if auto_approve else 0
    basename = os.path.basename(filename)
    url = "https://crowdin.com/project/khanacademy/{}/{}/upload?import_eq_suggestions=1&auto_approve_imported={}&qqfile={}".format(
        lang, fileid, auto_approve, basename)

    s = getCrowdinSession()
    with open(filename) as infile:
        response = s.post(url, data=infile)
    if response.json()["success"] != True:
        print("Submit failed: {}".format(response.text))
    # {success: true, version: "8"}
    # POST
    # content-type:application/octet-stream
    # x-file-name:test.xliff
    # x-requested-with:XMLHttpRequest

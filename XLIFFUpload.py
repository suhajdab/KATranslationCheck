#!/usr/bin/env python3
import requests
import os.path
from UpdateAllFiles import getCrowdinSession

def upload_file(filename, auto_approve=1, lang="lol"):
    fileid = 27579
    basename = os.path.basename(filename)
    url = "https://crowdin.com/project/khanacademy/{}/{}/upload?import_eq_suggestions=1&auto_approve_imported={}&qqfile={}".format(
        lang, fileid, auto_approve, basename)

    s = getCrowdinSession()
    with open(filename) as infile:
        response = s.post(url, data=infile)
    print(response.text)
    # {success: true, version: "8"}
    # POST
    # content-type:application/octet-stream
    # x-file-name:test.xliff
    # x-requested-with:XMLHttpRequest

if __name__ == "__main__":
    upload_file("/ram/test.xliff")
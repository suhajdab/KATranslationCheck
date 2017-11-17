#!/usr/bin/env python3
import requests
import os.path
import subprocess
from UpdateAllFiles import getCrowdinSession

def upload_file(filename, fileid, auto_approve=False, lang="lol", fullauto_account=False):
    auto_approve = 1 if auto_approve else 0
    basename = os.path.basename(filename)
    url = "https://crowdin.com/project/khanacademy/{}/{}/upload?import_eq_suggestions=1&{}qqfile={}".format(
        lang, fileid, "auto_approve_imported=1&" if auto_approve else "", basename)

    s = getCrowdinSession(fullauto_account=fullauto_account)
    with open(filename, "rb") as infile:
        response = s.post(url, data=infile)
    if response.json()["success"] != True:
        print("Submit failed: {}".format(response.text))
    # {success: true, version: "8"}
    # POST
    # content-type:application/octet-stream
    # x-file-name:test.xliff
    # x-requested-with:XMLHttpRequest

def update_crowdin_index_files(lang):
    """
    Update the ka-babelfish files on Crowdin
    """
    with open("apikey.txt") as infile:
        apikey = infile.read().strip()
    # Upload ifpatterns source
    out = subprocess.check_output(["curl",
        "-F", "files[ifpatterns.xliff]=@transmap/{}.ifpatterns.xliff".format(lang),
        "https://api.crowdin.com/api/project/ka-babelfish/update-file?key={}".format(apikey)])
    print(out)
    # Upload texttags source
    out = subprocess.check_output(["curl",
        "-F", "files[ifpatterns.xliff]=@transmap/{}.ifpatterns.xliff".format(lang),
        "https://api.crowdin.com/api/project/ka-babelfish/update-file?key={}".format(apikey)])
    print(out)

#!/usr/bin/env python3
import request
import os.path

def upload_file(filename, auto_approve=1):
    basename = os.path.basename(filename)
    url = "https://crowdin.com/project/khanacademy/lol/{}/upload?import_eq_suggestions=1&auto_approve_imported={}&qqfile={}".format(
        fileid, auto_approve, basename)
    # {success: true, version: "8"}
    # POST
    # content-type:application/octet-stream
    # x-file-name:test.xliff
    # x-requested-with:XMLHttpRequest
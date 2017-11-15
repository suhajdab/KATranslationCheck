#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Downloads lint files from an email account that has an abbonement for the KA i18n Google group.

WARNING: Use a dedicated email account. This script WILL delete other emails.
YOU HAVE BEEN WARNED!

Older emails and other emails will be deleted automatically.

Ensure the correct credentials are entered in imap-credentials.json (see imap-credentials-template.json).
"""
import re
import collections
import operator
from toolz.dicttoolz import valmap
from toolz.itertoolz import unique
from datetime import datetime
from email.parser import Parser
import os.path
import simplejson as json

KALintMail = collections.namedtuple('KALintMail', ["msgid", "subject", "date", "rfc822"])

def readEmailCredentials():
    with open("imap-credentials.json") as infile:
        return json.load(infile)

def fetchEMail(credentials):
    """
    Fetch all emails and delete old messages and other messages
    """
    from imapclient import IMAPClient
    rgx = re.compile(r"(\d+) crowdin entries linted for ([a-z]{2}(-[a-zA-Z]{2})?)")

    server = IMAPClient(credentials["host"], use_uid=True, ssl=True)
    server.login(credentials["user"], credentials["password"])

    select_info = server.select_folder('INBOX')
    print('{0} messages in INBOX'.format(select_info[b'EXISTS']))
    #Fetch list of emails
    messages = server.search(['NOT', 'DELETED'])
    msgmap = collections.defaultdict(list)
    # Fetch, filter and parse messages
    response = server.fetch(messages, ['BODY.PEEK[HEADER.FIELDS (SUBJECT)]', 'BODY.PEEK[HEADER.FIELDS (DATE)]', 'RFC822'])
    for msgid, data in response.items():
        try:
            subject = data[b'BODY[HEADER.FIELDS (SUBJECT)]'].decode("utf-8")
        except KeyError:
            continue
        if subject.startswith("Subject: "):
            subject = subject[len("Subject: "):]
        subject = subject.strip()
        # Date
        date = data[b'BODY[HEADER.FIELDS (DATE)]'].decode("utf-8").strip()
        if date.startswith("Date: "):
            date = date[len("Date: "):]
        if date.endswith("(PST)"):
            date = date[:-len("(PST)")].strip()
        if date.endswith("(PDT)"):
            date = date[:-len("(PDT)")].strip()
        if date.endswith("(UTC)"):
            date = date[:-len("(UTC)")].strip()
        if date.endswith("(CEST)"):
            date = date[:-len("(CEST)")].strip()
        if date.endswith("(EST)"):
            date = date[:-len("(EST)")].strip()
        try:
            date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
        except ValueError:
            date = datetime.strptime(date, "%d %b %Y %H:%M:%S %z")
        #
        match = rgx.match(subject)
        if not match: # Delete message
            print('   Deleting "{1}"'.format(msgid, subject))
            server.delete_messages(msgid)
        else:
            msgmap[match.group(2)].append(KALintMail(msgid, subject, date, data[b"RFC822"].decode("utf-8")))
    # Filter duplicates and sort by date
    msgmap = valmap(lambda vs: sorted(unique(vs, key=operator.attrgetter("msgid")), key=operator.attrgetter("date")), msgmap)
    # Delete old messages
    msgidsToDelete = set()
    for lang, values in msgmap.items():
        msgidsToDelete.update([v.msgid for v in values[:-1]])
    server.delete_messages(msgidsToDelete)
    print("Deleted {0} messages".format(len(msgidsToDelete)))
    # Remove old messages from msgmap (keep only latest)
    return valmap(operator.itemgetter(-1), msgmap)

def exportLintFile(val, directory="cache"):
    p = Parser()
    msg = p.parsestr(val.rfc822)
    m2 = msg.get_payload(1)
    filename = m2["Content-Disposition"].partition("filename=")[2].strip('"')
    csv = m2.get_payload(decode=True)
    ofilename = os.path.join(directory, filename)
    print("Exporting {0}".format(ofilename))
    with open(ofilename, "wb") as outfile:
        outfile.write(csv)

def exportLintFiles(msgmap):
    valmap(exportLintFile, msgmap)

def updateLintIMAPHandler(args):
    exportLintFiles(fetchEMail(readEmailCredentials()))

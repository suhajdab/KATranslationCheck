#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#******************************************************************************
# Copyright (C) 2015 Hitoshi Yamauchi
# New BSD License.
#******************************************************************************
# \file
# \brief Crowdin .po file filter
#
# Usecase:
#    Remove translated entries from the .po file
#
# Example:
#    Extract non-translated entries (keeps context)
#       ./pofilter.py sample.po -o sample.po.txt
#
#    Extract non-translated entries WITHOUT context line
#       ./pofilter.py --no-context sample.po sample.po.txt
#
import argparse, sys, re, codecs
import polib

def is_entry_untranslated(entry):
    """filter() function to determine if a given entry is"""
    return entry.msgid == entry.msgstr

def replace_msgstr_by_msgid(entry):
    entry.msgstr = entry.msgid
    # Fix comment not being exported
    entry.comment = entry.tcomment
    return entry

def remove_context_from_entry(entry):
    entry.comment = None
    entry.occurrences = []
    return entry

def find_untranslated_entries(infile, outfile, remove_context=False):
    """
    Read a PO file and find all untranslated entries.
    Note that polib's untranslated_entries() doesn't seem to work
    for Crowdin PO files.

    Returns a StringIO containing the resulting PO entries
    """
    poentries = polib.pofile(infile)
    # Find untranslated strings
    untranslated = filter(is_entry_untranslated, poentries)
    # Replace msgstr by msgid (because it would be empty otherwise due to POLib)
    export_entries = list(map(replace_msgstr_by_msgid, untranslated))
    # Remove context if enabled
    if remove_context:
        export_entries = list(map(remove_context_from_entry, export_entries))
    # Create a new PO with the entries
    result = polib.POFile()
    result.merge(export_entries)
    # Save to file
    result.save(outfile)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", type=str,
                        help="Input PO/POT file")

    parser.add_argument("outfile", type=str,
                        help="Output filename")

    parser.add_argument("-n", "--no-context", action="store_true",
                        help="Remove context from all strings")

    args = parser.parse_args()

    find_untranslated_entries(args.infile, args.outfile, args.no_context)


if __name__ == "__main__":
    try:
        main()
        # sys.exit()
    except RuntimeError as err:
        print('Runtime Error: {0}'.format(err))

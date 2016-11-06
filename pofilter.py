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

def id_to_str(entry):
    """filter() function to determine if a given entry is untranslated"""
    # Msgstr not empty OR both msgid and msgstr empty
    return (not entry.msgstr and entry.msgid)

def same(entry):
    """filter() function to determine if a given msgid is the same as the msgstr"""
    return entry.msgid == entry.msgstr


def differ(entry):
    """filter() function to determine if a given msgid is different to the msgstr"""
    return entry.msgid != entry.msgstr


def replace_msgstr_by_msgid(entry):
    return polib.POEntry(**{
        "msgid": entry.msgid,
        "msgstr": entry.msgid,
        "comment": entry.tcomment, # Fix comment not being written to output file
    })

filter_tools = {
    "id_to_str": id_to_str,
    "same": same,
    "differ": differ
}

map_tools = {
    "id_to_str": replace_msgstr_by_msgid,
    "same": lambda a: a,
    "differ": lambda a: a
}

def remove_context_from_entry(entry):
    entry.comment = None
    entry.occurrences = []
    return entry

def find_untranslated_entries(infile, remove_context=False, tool="id_to_str"):
    """
    Read a PO file and find all untranslated entries.
    Note that polib's untranslated_entries() doesn't seem to work
    for Crowdin PO files.

    Returns a string containing the resulting PO entries
    """
    poentries = polib.pofile(infile)
    # Find untranslated strings
    untranslated = filter(filter_tools[tool], poentries)
    # Replace msgstr by msgid (because it would be empty otherwise due to POLib)
    export_entries = list(map(map_tools[tool], untranslated))
    # Remove context if enabled
    if remove_context:
        export_entries = list(map(remove_context_from_entry, export_entries))
    # Create a new PO with the entries
    result = polib.POFile()
    [result.append(entry) for entry in export_entries]
    # Generate PO string
    return result.__unicode__()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", type=str,
                        help="Input PO/POT file")

    parser.add_argument("outfile", type=str, default="-", nargs="?",
                        help="Output filename (- is stdout)")

    parser.add_argument("--tool", choices=['id_to_str', 'same', 'differ'], default="id_to_str",
                        help="tools. id_to_str: copy msgid to msgstr. same: msgid == msgstr. differ: msgid != mgsstr")

    parser.add_argument("-n", "--no-context", action="store_true",
                        help="Remove context from all strings")

    args = parser.parse_args()

    postr = find_untranslated_entries(args.infile, args.no_context, args.tool)
    # Write or print to stdout
    if args.outfile == "-":
        print(postr)
    else:
        with open(args.outfile, "w") as outfile:
            outfile.write(postr)


if __name__ == "__main__":
    try:
        main()
        # sys.exit()
    except RuntimeError as err:
        print('Runtime Error: {0}'.format(err))

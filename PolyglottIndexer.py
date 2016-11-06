#!/usr/bin/env python3
from check import *
from ansicolor import black
import polib
from Languages import findAvailableLanguages

def loadTranslations(conn, recordTable=1, indexTable=2):
    """
    Loads all PO strings in the database and builds a Polyglott Index
    """
    print(black("Deleting old tables...", bold=True))
    # Delete old tables (implicitly closes tables)
    conn.deleteRange(recordTable, startKey=None, endKey=None)
    conn.deleteRange(indexTable, startKey=None, endKey=None)

    print(black("Deleting old tables...", bold=True))
    # Table 1 stores msgid => NUL-separated list of records
    #   Record: Langcode (KA-style) + ASCII record separator (0x1D) + msgstr
    conn.openTable(recordTable, mergeOperator="NULAPPEND")

    # Table 2 stores key => msgid
    #   where "key" is any msgid or msgstr.
    #   The appropriate values can be looked up in table 1 using the msgid key
    conn.openTable(indexTable, mergeOperator="REPLACE")

    for lang, langpath in findAvailableLanguages().items():
        print(black("Reading PO files for language {}".format(lang, bold=True)))
        for filename in findPOFiles(langpath):
            # NOTE: This loop writes one value dict per file per file to
            #  avoid tons of Python function calls.
            # The large values are be handled in C++ code efficiently.
            print("\tProcessing {}".format(filename))
            po = polib.pofile(filename)
            # Write table 1
            values = {entry.msgid: lang + "\x1D" + entry.msgstr
                      for entry in po if entry.msgstr.strip()}
            conn.put(recordTable, values)
            # Write table 2 (index)
            values = {entry.msgstr: entry.msgid for entry in po if entry.msgstr.strip()}
            values2 = {entry.msgid: entry.msgid for entry in po}
            conn.put(indexTable, values)
            conn.put(indexTable, values2)
    # Perform anticipatory compation on both tables
    print(black("Compacting language table...", bold=True))
    conn.compact(recordTable)
    print(black("Compacting index table...", bold=True))
    conn.compact(indexTable)

def buildPolyglottIndex(args):
    import YakDB
    print(black("Connecting to YakDB...", bold=True))

    conn = YakDB.Connection()
    conn.connect("tcp://localhost:7100")

    loadTranslations(conn, args.table, args.table + 1)

if __name__ == "__main__":
    buildPolyglottIndex(None)
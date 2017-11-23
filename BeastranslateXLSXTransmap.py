#!/usr/bin/env python3
from openpyxl import load_workbook
import json
import argparse
import functools
from AutoTranslateCommon import transmap_filename, to_xlsx
from AutoTranslationTranslator import FullAutoTranslator

def get_transmap(filename):
    wb = load_workbook(filename=filename)
    sheet = wb[wb.sheetnames[0]]
    tmap = {}
    for row in sheet.rows:
        if row[0].value == "Count": continue # Header
        count = int(row[0].value)
        utr_count = int(row[1].value)
        engl = row[2]
        transl = row[3]
        tmap[str(engl.value)] = str(transl.value)
    return [{"english": engl, "translated": transl, "count": count, "untranslated_count": utr_count}
            for engl,transl in tmap.items()]

def _translate(entry, translator, force=False):
    if not force and not entry["translated"]:
        return entry # leave as is
    transl = translator.translate(entry["english"])
    entry["translated"] = transl
    print("{} ==> {}".format(entry["english"], entry["translated"]))
    return entry


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l','--language', help='The language')
    parser.add_argument('iftags', help='The IF tags XLSX file')
    parser.add_argument('texttags', help='The text tags XLSX file')
    args = parser.parse_args()

    iftags = get_transmap(args.iftags)
    texttags = get_transmap(args.texttags)
    print("Found {} iftags".format(len(iftags)))
    print("Found {} text tags".format(len(texttags)))

    # Translate them
    fat = FullAutoTranslator(args.language, limit=1000000)
    _do = functools.partial(_translate, translator=fat)
    iftags = list(map(_do, iftags))
    texttags = list(map(_do, texttags))

    iftagsFile = args.iftags.replace(".xlsx", ".translated.xlsx")
    texttagsFile = args.texttags.replace(".xlsx", ".translated.xlsx")
    print("Exporting IF tags to {}".format(iftagsFile))
    print("Exporting text tags to {}".format(texttagsFile))

    to_xlsx(iftags, iftagsFile)
    to_xlsx(texttags, texttagsFile)

#!/usr/bin/env python3
"""
export GOOGLE_APPLICATION_CREDENTIALS=/home/uli/dev/KATranslationCheck/Babelfish\ Full\ Auto\ Dev-88b1b9fc498f.json
"""
from googletrans import Translator
#from google.cloud import translate
import re

def placeholder(n):
    return "XXXYYY{}YYYXXX".format(n)

def can_be_translated(s):
    if "\\text" in s:
        return False
    if "\\mathrm" in s:
        return False
    if "*" in s:
        return False
    if "\\n" in s:
        return False
    return True

def preproc(s):
    _formula_re = re.compile(r"\$[^\$]+\$")
    # Forward-replace
    n = 0
    formulaMap = {}
    while True:
        match = _formula_re.search(s)
        if match is None: # No more formulas
            break
        formula = match.group(0)
        current_placeholder = placeholder(n)
        formulaMap[current_placeholder] = formula
        s = _formula_re.sub(current_placeholder, s, count=1)
        n += 1
    return s, formulaMap

def postproc(s, fmap):
    """
    Back-replce placeholders
    """
    for placeholder, rep in fmap.items():
        s = s.replace(placeholder, rep)
    return s

def google_translate(txt, lang="de"):
    translator = Translator()
    #translate_client = translate.Client()
    #translation = translate_client.translate( txt, target_language=lang)
    result = translator.translate(txt, src="en", dest="de")
    return result.text
    #return translation['translatedText']

def full_auto_translate(s, lang="de"):
    # Ignore currently unhandled cases
    if not can_be_translated(s):
        return None
    # Replace formulas etc. by placeholders
    txt, formula_map = preproc(s)
    # Check validity of placeholders (should yield original string)
    assert postproc(txt, formula_map) == s
    # Perform translation
    translated = google_translate(txt, lang)
    # Back-replace placeholders
    txt2 = postproc(translated, formula_map)
    return txt2

#print(google_translate('The graph of $r$ has no vertical tangents.'))
print(full_auto_translate('The graph of $r$ has no vertical tangents.'))
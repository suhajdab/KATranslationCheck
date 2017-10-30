#!/usr/bin/env python3
import re as re
from collections import Counter, defaultdict
from ansicolor import red

class CompositeAutoTranslator(object):
    """
    Utility that calls tries all autoindexers until one is able to translate
    the string.
    """
    def __init__(self, *args):
        self.children = list(filter(lambda arg: arg is not None, args))

    def translate(self, engl):
        for child in self.children:
            result = child.translate(engl)
            if result is not None:  # Could translate
                return result
        return None

class RuleAutotranslator(object):
    """
    Auto-translates based on regex rules.
    Will mostly auto-translate formula-only etc
    """
    def __init__(self):
        # Formulas:
        #   $...$
        #    **$...$
        self._is_formula = re.compile(r"^>?[\s\*]*(\$[^\$]+\$(\s|\\n|\*)*)+$");
        # contains a \text{ clause except specific text clauses:
        #   \text{ cm}
        #   \text{ m}
        #   \text{ g}
        self._contains_text = re.compile(r"\\text\{(?! ?cm\})(?! ?m\})(?! ?g\})(?! ?kg\})");
        # URLs:
        #   ![](web+graphie://ka-perseus-graphie.s3.amazonaws.com/...)
        #   web+graphie://ka-perseus-graphie.s3.amazonaws.com/...
        #   https://ka-perseus-graphie.s3.amazonaws.com/...png
        self._is_perseus_img_url = re.compile(r"^(!\[\]\()?\s*(http|https|web\+graphie):\/\/ka-perseus-(images|graphie)\.s3\.amazonaws\.com\/[0-9a-f]+(\.(svg|png|jpg))?\)?\s*$")

        self._is_formula_plus_img = re.compile(r"^>?[\s\*]*(\$[^\$]+\$(\s|\\n|\*)*)+(!\[\]\()?\s*(http|https|web\+graphie):\/\/ka-perseus-(images|graphie)\.s3\.amazonaws\.com\/[0-9a-f]+(\.(svg|png|jpg))?\)?\s*$")

    def translate(self, engl):
        is_formula = self._is_formula.match(engl) is not None
        contains_text = self._contains_text.search(engl) is not None
        is_perseus_img_url = self._is_perseus_img_url.match(engl) is not None
        is_formula_plus_img = self._is_formula_plus_img.match(engl) is not None

        if is_formula and not contains_text:
            return engl
        if is_perseus_img_url or is_formula_plus_img:
            return engl

class NameAutotranslator(object):
    """
    Auto-translates based on regex rules.
    Will mostly auto-translate formula-only etc
    """
    def __init__(self, lang):
        self.lang = lang
        self._re1 = re.compile(r"^\s*Only\s+([A-Z][a-z]+)((\.|\s+|\\n)*)$")
        self._re2 = re.compile(r"^\s*Neither\s+([A-Z][a-z]+)\s+nor\s+([A-Z][a-z]+)((\.|\s+|\\n)*)$")
        self._re3 = re.compile(r"^\s*Either\s+([A-Z][a-z]+)\s+or\s+([A-Z][a-z]+)((\.|\s+|\\n)*)$")
        self._re4 = re.compile(r"^\s*Both\s+([A-Z][a-z]+)\s+and\s+([A-Z][a-z]+)((\.|\s+|\\n)*)$")
        self._re5 = re.compile(r"^\s*Neither\s+([A-Z][a-z]+)\s+nor\s+([A-Z][a-z]+)\s+are\s+correct((\.|\s+|\\n)*)$")
        self._re6 = re.compile(r"^\s*Both\s+([A-Z][a-z]+)\s+and\s+([A-Z][a-z]+)\s+are\s+correct((\.|\s+|\\n)*)$")
        # Translation patterns in this order:
        #   Only <name1>
        #   Neither <name1> nor <name2>
        #   Either <name1> or <name2>
        #   Both <name1> and <name2>
        #   Neither <name1> nor <name2> are correct
        #   Both <name1> and <name2> are correct
        transmap = {
            "sv-SE": [
                "Endast <name1>",
                "Varken <name1> eller <name2>",
                "Antingen <name1> eller <name2>",
                "Både <name1> och <name2>",
                "Varken <name1> eller <name2> är korrekta",
                "Både <name1> och <name2> är korrekta"
            ]
        }
        if lang not in transmap:
            raise "Please create name translation mapping for {}".format(lang)
        self.transmap = transmap[lang]

    def replace_name(self, lang, name):
        """
        Get the localized replacement name
        """
        # TODO not implemented
        return name

    def translate(self, engl):
        m1 = self._re1.match(engl)
        m2 = self._re2.match(engl)
        m3 = self._re3.match(engl)
        m4 = self._re4.match(engl)
        m5 = self._re5.match(engl)
        m6 = self._re6.match(engl)
        if m1:
            name1 = m1.group(1)
            rest = m1.group(2)
            return self.transmap[0].replace("<name1>", name1) + rest
        elif m2:
            name1 = m2.group(1)
            name2 = m2.group(2)
            rest = m2.group(3)
            return self.transmap[1].replace("<name1>", name1).replace("<name2>", name2) + rest
        elif m3:
            name1 = m3.group(1)
            name2 = m3.group(2)
            rest = m3.group(3)
            return self.transmap[2].replace("<name1>", name1).replace("<name2>", name2) + rest
        elif m4:
            name1 = m4.group(1)
            name2 = m4.group(2)
            rest = m4.group(3)
            return self.transmap[3].replace("<name1>", name1).replace("<name2>", name2) + rest
        elif m5:
            name1 = m5.group(1)
            name2 = m5.group(2)
            rest = m5.group(3)
            return self.transmap[4].replace("<name1>", name1).replace("<name2>", name2) + rest
        elif m6:
            name1 = m6.group(1)
            name2 = m6.group(2)
            rest = m6.group(3)
            return self.transmap[5].replace("<name1>", name1).replace("<name2>", name2) + rest




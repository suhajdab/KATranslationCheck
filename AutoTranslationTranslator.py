#!/usr/bin/env python3
import re as re
from collections import Counter, defaultdict, namedtuple
from ansicolor import red
import os.path
import json
from toolz.dicttoolz import merge
from AutoTranslateCommon import *
from googletrans import Translator

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
        self._is_formula = re.compile(r"^(>|#)*[\s\*]*(\$[^\$]+\$(\s|\\n|\*)*)+$");
        # contains a \text{ clause except specific text clauses:
        #   \text{ cm}
        #   \text{ m}
        #   \text{ g}
        self._contains_text = get_text_regex()
        # URLs:
        #   ![](web+graphie://ka-perseus-graphie.s3.amazonaws.com/...)
        #   web+graphie://ka-perseus-graphie.s3.amazonaws.com/...
        #   https://ka-perseus-graphie.s3.amazonaws.com/...png
        self._is_perseus_img_url = re.compile(r"^(!\[\]\()?\s*(http|https|web\+graphie):\/\/ka-perseus-(images|graphie)\.s3\.amazonaws\.com\/[0-9a-f]+(\.(svg|png|jpg|jpeg))?\)?\s*$")

        self._is_formula_plus_img = re.compile(r"^>?[\s\*]*(\$[^\$]+\$(\s|\\n|\*)*)+(!\[\]\()?\s*(http|https|web\+graphie):\/\/ka-perseus-(images|graphie)\.s3\.amazonaws\.com\/[0-9a-f]+(\.(svg|png|jpg))?\)?\s*$")
        self._is_input = re.compile(r"^\[\[\s*☃\s*[a-z-]+\s*\d*\s*\]\](\s|\\n)*$", re.UNICODE)
        self._is_formula_plus_input = re.compile(r"^(>|#)*[\s\*]*(\$[^\$]+\$(\s|\\n|\*)*)+=?\s*\[\[\s*☃\s*[a-z-]+\s*\d*\s*\]\](\s|\\n)*$", re.UNICODE);
        self._is_simple_coordinate = re.compile(r"^[\[\(]-?\d+,-?\d+[\]\)]$")

    def translate(self, engl):
        is_formula = self._is_formula.match(engl) is not None
        contains_text = self._contains_text.search(engl) is not None
        is_perseus_img_url = self._is_perseus_img_url.match(engl) is not None
        is_formula_plus_img = self._is_formula_plus_img.match(engl) is not None
        is_formula_plus_input = self._is_formula_plus_input.match(engl) is not None
        is_input = self._is_input.match(engl) is not None
        is_simple_coordinate = self._is_simple_coordinate.match(engl) is not None

        if is_perseus_img_url or is_formula_plus_img or is_input or is_formula_plus_input or is_simple_coordinate:
            return engl
        if is_formula and not contains_text:
            return engl

class IFPatternAutotranslator(object):
    """
    Ignore Formula pattern autotranslator
    """
    def __init__(self, lang):
        self.lang = lang
        # Read patterns index
        self.ifpatterns = read_ifpattern_index(lang)
        self.texttags = read_texttag_index(lang)
        # Compile regexes
        self._formula_re = re.compile(r"\$[^\$]+\$")
        self._img_re = get_image_regex()
        self._text = get_text_content_regex()

    def translate(self, engl):
        # Normalize and filter out formulae with translatable text
        normalized = self._formula_re.sub("§formula§", engl)
        normalized = self._img_re.sub("§image§", normalized)
        # Mathrm is a rare alternative to \\text which is unhanled at the moment
        if "mathrm" in engl:
            return None
        # If there are any texts, check if we know how to translate
        texttag_replace = {} # texttags: engl full tag to translated full tag 
        for text_hit in self._text.finditer(engl):
            content = text_hit.group(2).strip()
            if content in self.texttags:
                # Assemble the correct replacement string
                translated = text_hit.group(1) + self.texttags[content] + text_hit.group(3)
                texttag_replace[text_hit.group(0)] = translated
            else: # Untranslatable tag
                return None # Cant fully translate this string
        # Check if it matches
        if normalized not in self.ifpatterns:
            return None # Do not have pattern
        transl = self.ifpatterns[normalized]
        # Find formulae in english text
        #
        # Replace one-by-one
        #
        src_formulae = self._formula_re.findall(engl)
        while "§formula§" in transl:
            next_formula = src_formulae.pop(0) # Next "source formula"
            transl = transl.replace("§formula§", next_formula, 1)
        
        src_images = self._img_re.findall(engl)
        while "§image§" in transl:
            next_image = src_images.pop(0)[0] # Next "source image"
            transl = transl.replace("§image§", next_image, 1)
        # Translate text-tags, if any
        for src, repl in texttag_replace.items():
            # Safety: If there is nothing to replace, fail instead of
            # failing to translate a text tag
            if src not in transl:
                print(red("Text-tag translation: Can't find '{}' in '{}'".format(
                    src, transl), bold=True))
                return None
            transl = transl.replace(src, repl)
        return transl


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
        self._re7 = re.compile(r"^\s*Yes,\s+([A-Z][a-z]+)\s+is\s+correct\s+but\s+([A-Z][a-z]+)\s+is\s+not((\.|\s+|\\n)*)$")
        self._re8 = re.compile(r"^\s*In conclusion,\s*([A-Z][a-z]+)\s+is\s+correct((\.|\s+|\\n)*)$")
        self._re9 = re.compile(r"^\s*Only\s*([A-Z][a-z]+)\s+is\s+correct((\.|\s+|\\n)*)$")
        self._re10 = re.compile(r"^\s*([A-Z][a-z]+)'s\s+work\s+is\s+correct((\.|\s+|\\n)*)$")
        # Translation patterns in this order:
        #   1. Only <name1>
        #   2. Neither <name1> nor <name2>
        #   3. Either <name1> or <name2>
        #   4. Both <name1> and <name2>
        #   5. Neither <name1> nor <name2> are correct
        #   6. Both <name1> and <name2> are correct
        #   7. Yes, <name1> is correct but <name2> is not
        #   8. In conclusion, <name1> is correct
        #   9. Only <name1> is correct
        #   10.<name1>'s work is correct
        transmap = {
            "sv-SE": [
                "Endast <name1>",
                "Varken <name1> eller <name2>",
                "Antingen <name1> eller <name2>",
                "Både <name1> och <name2>",
                "Varken <name1> eller <name2> har rätt",
                "Både <name1> och <name2> har rätt",
                "Ja, <name1> har rätt men inte <name2>",
                "Avslutningsvis, så har <name1> rätt",
                "Endast <name1> har rätt",
                "<name1>s lösning är rätt"

            ], "lol": [
                "Only <name1>",
                "Neither <name1> norz <name2>",
                "Either <name1> or <name2>",
                "Both <name1> and <name2>",
                "Neither <name1> nor <name2> are correct",
                "Both <name1> and <name2> are correct"
            ], "de": [
                "Nur <name1>",
                "Weder <name1> noch <name2>",
                "Entweder <name1> oder <name2>",
                "Sowohl <name1> als auch <name2>",
                "Weder <name1> noch <name2> liegen richtig",
                "Sowohl <name1> als auch <name2> liegt richig",
                "Ja, <name1> liegt richtig, aber <name2> liegt falsch",
                "Zusammenfassend liegt <name1> richtig",
                "Nur <name1> liegt richtig",
                "Die Lösung von <name1> ist korrekt"
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

    def _translate_match_two_names(self, m, transmap_entry):
        name1 = m.group(1)
        name2 = m.group(2)
        rest = m.group(3)
        return transmap_entry.replace("<name1>", name1).replace("<name2>", name2) + rest

    def _translate_match_one_name(self, m, transmap_entry):
        if transmap_entry is None: # Unknown translation
            return None # Cant translate
        name1 = m.group(1)
        rest = m.group(2)
        return transmap_entry.replace("<name1>", name1) + rest

    def translate(self, engl):
        m1 = self._re1.match(engl)
        m2 = self._re2.match(engl)
        m3 = self._re3.match(engl)
        m4 = self._re4.match(engl)
        m5 = self._re5.match(engl)
        m6 = self._re6.match(engl)
        m7 = self._re7.match(engl)
        m8 = self._re8.match(engl)
        m9 = self._re9.match(engl)
        m10 = self._re10.match(engl)
        if m1:
            return self._translate_match_one_name(m1, self.transmap[0])
        elif m2:
            return self._translate_match_two_names(m2, self.transmap[1])
        elif m3:
            return self._translate_match_two_names(m3, self.transmap[2])
        elif m4:
            return self._translate_match_two_names(m4, self.transmap[3])
        elif m5:
            return self._translate_match_two_names(m5, self.transmap[4])
        elif m6:
            return self._translate_match_two_names(m6, self.transmap[5])
        elif m7:
            return self._translate_match_two_names(m7, self.transmap[6])
        elif m8:
            return self._translate_match_one_name(m8, self.transmap[7])
        elif m9:
            return self._translate_match_one_name(m9, self.transmap[8])
        elif m10:
            return self._translate_match_one_name(m10, self.transmap[9])

PlaceholderInfo = namedtuple("PlaceholderInfo", [
    "nPlaceholders", "replaceMap", "nAsterisks", "nNewlines"])

class FullAutoTranslator(object):
    """
    Google translate based full auto translator
    """
    def __init__(self, lang, limit=25):
        self.lang = lang if lang != "lol" else "de" # LOL => translate to DE
        self._formula_re = re.compile(r"\s*\$[^\$]+\$\s*")
        self._asterisk_re = re.compile(r"\s*\*+\s*")
        self._newline_re = re.compile(r"\s*(\\n)+\s*")
        self._input_re = re.compile(r"\s*\[\[☃\s+[a-z-]+\s*\d*\]\]\s*")
        self._image_re = re.compile(r"\s*!\[([^\]]*)\]\(\s*(http|https|web\+graphie):\/\/ka-perseus-(images|graphie)\.s3\.amazonaws\.com\/[0-9a-f]+(\.(svg|png|jpg|jpeg))?\)\s*")
        self.limit = limit
        self.dbgout = open("fullauto-dbg.txt", "w")
        self.uchars = "■□▢▣▤▥▦▧▨▩▪▫▬▭▮▯▰▱▲△▴▵▶▷▸▹►▻▼▽▾▿◀◁◂◃◄◅◆◇◈◉◊○◌◍◎●◐◑◒◓◔◕◖◗◘◙◚◛◜◝◞◟◠◡◢◣◤◥◧◨◩◪◫◬◭◮◯◰◱◲◳◴◵◶◷◸◹◺◻◼◽◿◾"

    def __del__(self):
        self.dbgout.close()

    def proto_placeholder(self, n):
        return self.uchars[n]

    def placeholder(self, n):
        #return self.uchars[n]
        return "52472451639{}13742".format(n)

    def can_be_translated(self, s):
        if "\\text" in s:
            return False
        if "\\textit" in s:
            return False
        if "\\$" in s:
            return False
        if "+" in s:
            return False
        if "%(" in s:
            return False
        if "\\mathrm" in s:
            return False
        if "`" in s:
            return False
        return True

    def placeholder_replace(self, s, n, re):
        repmap = {}
        while True:
            match = re.search(s)
            if match is None: # No more formulas
                break
            formula = match.group(0)
            current_placeholder = self.proto_placeholder(n)
            repmap[current_placeholder] = formula
            # Add spaces before and after placeholder to separate from other elements of text
            s = re.sub(current_placeholder, s, count=1)
            n += 1
        return s, repmap, n

    def final_replace(self, s, n):
        """
        Replace proto placeholders by final placeholders
        """
        for i in range(n):
            s = s.replace(self.proto_placeholder(i), " {} ".format(self.placeholder(i)))
        return s


    def first_stage_backreplace(self, s, n):
        """
        Replace proto placeholders by final placeholders
        """

        for i in range(n):
            placeholder = self.placeholder(i)
            # Check if it got mis-translated...
            if placeholder not in s:
                print(red("{} not found in '{}'".format(placeholder, s), bold=True))
                return None
            # Replace by proto-placeholder which is a unicode char
            s = re.sub(r"\s*" + placeholder + r"\s*",
                self.proto_placeholder(i), s, flags=re.UNICODE)
        return s

    def check_no_placeholders_left(self, s):
        for c in self.uchars:
            if c in s:
                print(red("Found placeholder {} in '{}'".format(c, s), bold=True))
                return True
        return False

    def combo_count(self, s, char):
        return [s.count(char * n) for n in range(1, 10)]

    def back_replace(self, s, repmap):
        """
        Like simple_replace, but replaces
        """
        for placeholder, rep in repmap.items():
            s = s.replace(placeholder, rep)
        return s

    def preproc(self, s):
        """
        Forward-replace first with proto-placeholders to avoid impacting

        As proto-placeholders are unicode chars and will often be touched by the translator,
        we then replace them by final numeric code placeholders with whitespace
        added before and after which are not touched.
        """
        n = 0

        # \\n or might be directly followed by a word character and might be screwed up
        # We count their number of newline combos now to check restoration later.
        nAsterisks = self.combo_count(s, "*")
        nNewlines = self.combo_count(s, "\\n")

        s, formulaMap, n = self.placeholder_replace(s, n, self._formula_re)
        s, asteriskMap, n = self.placeholder_replace(s, n, self._asterisk_re)
        s, newlineMap, n = self.placeholder_replace(s, n, self._newline_re)
        s, inputMap, n = self.placeholder_replace(s, n, self._input_re)
        s, imgMap, n = self.placeholder_replace(s, n, self._image_re)

        repmap = merge(formulaMap, asteriskMap, newlineMap, inputMap, imgMap)

        # Final placeholder replacement
        s = self.final_replace(s, n)

        return s, PlaceholderInfo(n, repmap, nAsterisks, nNewlines)

    def postproc(self, engl, s, info):
        """
        Back-replace placeholders
        """
        # Replace numeric placeholders by unicode placeholders
        # This prevents spaces between placeholders cross-affecting each other
        s = self.first_stage_backreplace(s, info.nPlaceholders)
        if s is None:  # Placeholder missing or changed
            return None

        # Replace unicode placeholders by their original value
        s = self.back_replace(s, info.replaceMap)

        # Now no placeholders should be left
        if self.check_no_placeholders_left(s):
            return None

        #
        # Check if combinations match
        #
        nAsterisksNew = self.combo_count(s, "*")
        if nAsterisksNew != info.nAsterisks:
            print(red("* not reconstructed in '{}' engl '{}'".format(s, engl), bold=True))
            return None

        nNewlinesNew = self.combo_count(s, "\\n")
        if nNewlinesNew != info.nNewlines:
            print(red("\\n not reconstructed in '{}' engl '{}'".format(s, engl), bold=True))
            return None
        return s

    def google_translate(self, txt):
        translator = Translator()
        #translate_client = translate.Client()
        #translation = translate_client.translate( txt, target_language=lang)
        #return translation['translatedText']
        # partition: sv-SE => sv
        result = translator.translate(txt, src="en", dest=self.lang.partition("-")[0])
        return result.text

    def translate(self, engl):
        # Use limit on how much to translate at once
        if self.limit <= 0:
            return None # dont translate
        self.limit -= 1
        # Ignore currently unhandled cases
        if not self.can_be_translated(engl):
            return None
        # Replace formulas etc. by placeholders
        engl_proc, info = self.preproc(engl)
        # Check validity of placeholders (should yield original string)
        test_postproc = self.postproc(engl, engl_proc, info)
        if test_postproc != engl:
            print(red("Test reproc failed: '{}' instead of '{}'".format(test_postproc, engl)))
            return None
        # Perform translation
        translated = self.google_translate(engl_proc)
        # Back-replace placeholders
        txt2 = self.postproc(engl, translated, info)
        # Emit debug data
        print("{", file=self.dbgout)
        print("\tEngl:",engl, file=self.dbgout)
        print("\tMap:",info.replaceMap, file=self.dbgout)
        print("\tPreproc:", engl_proc, file=self.dbgout)
        print("\tTranslated:", translated, file=self.dbgout)
        print("\tResult:", txt2, file=self.dbgout)
        print("}", file=self.dbgout)
        return txt2

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('string', help='The string to translate')
    args = parser.parse_args()

    fa = FullAutoTranslator("de")
    print(fa.translate(args.string))
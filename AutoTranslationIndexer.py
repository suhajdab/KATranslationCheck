#!/usr/bin/env python3
import re as re
from collections import Counter, defaultdict
from ansicolor import red
from toolz.dicttoolz import valmap
from AutoTranslationTranslator import RuleAutotranslator
import os
import json
from AutoTranslateCommon import *

class CompositeIndexer(object):
    """
    Utility that calls add() once for every child object.
    So you dont need to change indexers all over the place.

    Args are filtered for None
    """
    def __init__(self, *args):
        self.children = list(filter(lambda arg: arg is not None, args))

    def add(self, *args, **kwargs):
        for child in self.children:
            child.add(*args, **kwargs)

class TextTagIndexer(object):
    def __init__(self, lang):
        self.lang = lang
        self.index = Counter() # UNTRANSLATED count for each text tag
        self.translated_index = defaultdict(Counter)
        self._re = re.compile(r"\\text\s*\{\s*([^\}]+)\}")

    def add(self, engl, translated=None, filename=None):
        # Find english hits and possible hits in target lang to be able to match them!
        engl_hits = self._re.finditer(engl)
        # Just make sure that transl_hits has the same length as index
        transl_hits = None if translated is None else self._re.finditer(translated)
        # Find hits in english
        if translated is not None: # Translated, do not count but index
            for engl_hit, transl_hit in zip(engl_hits, transl_hits):
                # Extract corresponding hits
                engl_hit = engl_hit.group(1).strip()
                transl_hit = transl_hit.group(1).strip()
                # Count
                self.index[engl_hit] += 1
                # If untranslated, do not index translions
                if transl_hit:
                    self.translated_index[engl_hit][transl_hit] += 1
        #except Exception as ex:
        #    print(red("Failed to index '{}' --> {}: {}".format(engl, translated, ex) bold=True))

    def __len__(self):
        return len(self.index)

    def exportJSON(self):
        texttags = []
        for (hit, count) in self.index.most_common():
            # Get the most common translation for that tag
            transl = "" if len(self.translated_index[hit]) == 0 \
                else self.translated_index[hit].most_common(1)[0][0]
            texttags.append({"english": hit, "translated": transl, "count": count, "type": "texttag"})

        # Export main patterns file
        with open(transmap_filename(self.lang, "texttags"), "w") as outfile:
            json.dump(texttags, outfile, indent=4, sort_keys=True)

        # export file of untranslated patterns
        with open(transmap_filename(self.lang, "texttags.untranslated"), "w") as outfile:
            json.dump(list(filter(lambda p: not p["translated"], texttags)),
                outfile, indent=4, sort_keys=True)

class IgnoreFormulaPatternIndexer(object):
    """
    Indexes patterns with only the text as key, replacing all formulas with <formula>
    """
    def __init__(self, lang):
        self.lang = lang
        self.autotrans = RuleAutotranslator()
        self.index = Counter()
        self.translated_index = defaultdict(Counter)
        self._formula_re = re.compile(r"\$[^\$]+\$")
        self._text = get_text_regex()
        # Ignore specific whitelisted texts which are not translated

    def add(self, engl, translated=None, filename=None):
        normalized_engl = self._formula_re.sub("<formula>", engl)

        has_text = self._text.search(engl)
        if has_text: # Currently ignore
            # TODO Maybe we have a translation for the text?
            return

        # Count also if translated
        self.index[normalized_engl] += 1
        # Track translation for majority selection later
        if translated is not None:
            normalized_trans = self._formula_re.sub("<formula>", translated)
            self.translated_index[normalized_engl][normalized_trans] += 1

    def exportJSON(self):
        ifpatterns = []
        for (hit, count) in self.index.most_common():
            # Get the most common pattern
            transl = "" if len(self.translated_index[hit]) == 0 \
                else self.translated_index[hit].most_common(1)[0][0]
            if count >= 2:  # Ignore non-patterns
                ifpatterns.append({"english": hit, "translated": transl, "count": count, "type": "ifpattern"})

        # Export main patterns file
        with open(transmap_filename(self.lang, "ifpatterns"), "w") as outfile:
            json.dump(ifpatterns, outfile, indent=4, sort_keys=True)

        # export file of untranslated patterns
        with open(transmap_filename(self.lang, "ifpatterns.untranslated"), "w") as outfile:
            json.dump(list(filter(lambda p: not p["translated"], ifpatterns)),
                outfile, indent=4, sort_keys=True)

class GenericPatternIndexer(object):
    """
    Indexes arbitrary patters with unknown form by replacing ndoes
    """
    def __init__(self):
        self.index = Counter()
        self.translated_index = {}
        self.autotranslator = RuleAutotranslator()
        self._re = re.compile(r"\d")

    def add(self, engl, translated=None, filename=None):
        # If the autotranslator can translate it, ignore it
        if self.autotranslator.translate(engl) is not None:
            return
        # Currently just remove digits
        normalized = self._re.sub("<num>", engl)
        # Add to index
        self.index[normalized] += 1
        # Add translated version to index
        if translated:
            self.translated_index[normalized] = self._re.sub("<num>", translated)

    def exportCSV(self, filename):
        with open(filename, "w") as outfile:
            for (hit, count) in self.index.most_common():
                transl = self.translated_index[hit] if hit in self.translated_index else ""
                outfile.write("\"{}\",\"{}\",{}\n".format(hit,transl,count))

class NamePatternIndexer(object):
    """
    Indexes patterns like "Only Olof and Uli"
    and generates a list of names from that.
    """
    def __init__(self):
        self.index = Counter()
        self.translated_patterns = [None, None, None, None] # Translations of pattern 1..4
        self._re1 = re.compile(r"^\s*Only\s+([A-Z][a-z]+)(\.|\s+|\\n)*$")
        self._re2 = re.compile(r"^\s*Neither\s+([A-Z][a-z]+)\s+nor\s+([A-Z][a-z]+)(\.|\s+|\\n)*$")
        self._re3 = re.compile(r"^\s*Either\s+([A-Z][a-z]+)\s+or\s+([A-Z][a-z]+)(\.|\s+|\\n)*$")
        self._re4 = re.compile(r"^\s*Both\s+([A-Z][a-z]+)\s+and\s+([A-Z][a-z]+)(\.|\s+|\\n)*$")

    def add(self, engl, translated=None, filename=None):
        m1 = self._re1.match(engl)
        m2 = self._re2.match(engl)
        m3 = self._re3.match(engl)
        m4 = self._re4.match(engl)
        if m1:
            name1 = m1.group(1)
            self.index[name1] += 1
            if translated is not None and name1 in translated:
                self.translated_patterns[0] = translated.replace(name1, "<name1>")
        if m2:
            name1 = m2.group(1)
            name2 = m2.group(2)
            self.index[name1] += 1
            self.index[name2] += 1
            if translated is not None and name1 in translated and name2 in translated:
                self.translated_patterns[1] = \
                    translated.replace(name1, "<name1>").replace(name2, "<name2>")
        if m3:
            name1 = m3.group(1)
            name2 = m3.group(2)
            self.index[name1] += 1
            self.index[name2] += 1
            if translated is not None and name1 in translated and name2 in translated:
                self.translated_patterns[2] = \
                    translated.replace(name1, "<name1>").replace(name2, "<name2>")
        if m4:
            name1 = m4.group(1)
            name2 = m4.group(2)
            self.index[name1] += 1
            self.index[name2] += 1
            if translated is not None and name1 in translated and name2 in translated:
                self.translated_patterns[3] = \
                    translated.replace(name1, "<name1>").replace(name2, "<name2>")

    def __len__(self):
        cnt = 0
        for (_, count) in self.index.most_common():
            cnt += count
        return cnt

    def printTranslationPattern(self, lang):
        print("Name translation patterns for {}:\n\t{}\n\t{}\n\t{}\n\t{}".format(lang,
            self.translated_patterns[0],
            self.translated_patterns[1],
            self.translated_patterns[2],
            self.translated_patterns[3]))

    def exportCSV(self, filename):
        with open(filename, "w") as outfile:
            for (hit, count) in self.index.most_common():
                outfile.write("\"{}\",{}\n".format(hit, count))

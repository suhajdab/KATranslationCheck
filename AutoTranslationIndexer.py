#!/usr/bin/env python3
import re as re
from collections import Counter, defaultdict
from ansicolor import red
from toolz.dicttoolz import valmap
from AutoTranslationTranslator import RuleAutotranslator
import os
import json
from bs4 import BeautifulSoup
from UpdateAllFiles import getTranslationFilemapCache
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
        self.index = Counter() # TOTAL count for each text tag
        self.untranslated_index = Counter()
        self.translated_index = defaultdict(Counter)
        self._re = get_text_content_regex()

    def add(self, engl, translated=None, filename=None):
        # Find english hits and possible hits in target lang to be able to match them!
        engl_hits = self._re.finditer(engl)
        # Just make sure that transl_hits has the same length as index
        transl_hits = None if translated is None else self._re.finditer(translated)
        # Find hits in english
        if translated is not None: # Translated, do not count but index
            for engl_hit, transl_hit in zip(engl_hits, transl_hits):
                # Extract corresponding hits
                engl_hit = engl_hit.group(2).strip()
                transl_hit = transl_hit.group(2).strip()
                # Count
                self.index[engl_hit] += 1
                # If untranslated, do not index translions
                if transl_hit:
                    self.translated_index[engl_hit][transl_hit] += 1
        else: # Not translated, just index to collect stats
            for engl_hit in engl_hits:
                engl_hit = engl_hit.group(2).strip()
                self.index[engl_hit] += 1
                self.untranslated_index[engl_hit] += 1
        #except Exception as ex:
        #    print(red("Failed to index '{}' --> {}: {}".format(engl, translated, ex) bold=True))

    def __len__(self):
        return len(self.index)

    def _convert_to_json(self, ignore_alltranslated=False):
        texttags = []
        for (hit, count) in self.index.most_common():
            untransl_count = self.untranslated_index[hit]
            if untransl_count == 0 and ignore_alltranslated:
                continue
            # Get the most common translation for that tag
            transl = "" if len(self.translated_index[hit]) == 0 \
                else self.translated_index[hit].most_common(1)[0][0]
            texttags.append({"english": hit,
                "translated": transl, "count": count,
                "untranslated_count": untransl_count,
                "type": "texttag"})
        return texttags


    def exportJSON(self, ignore_alltranslated=False):
        texttags = self._convert_to_json(ignore_alltranslated)
        # Export main patterns file
        with open(transmap_filename(self.lang, "texttags"), "w") as outfile:
            json.dump(texttags, outfile, indent=4, sort_keys=True)

        # export file of untranslated patterns
        with open(transmap_filename(self.lang, "texttags.untranslated"), "w") as outfile:
            json.dump(list(filter(lambda p: not p["translated"], texttags)),
                outfile, indent=4, sort_keys=True)

    def exportXLIFF(self, ignore_alltranslated=False):
        texttags = self._convert_to_json(ignore_alltranslated)
        soup = pattern_list_to_xliff(texttags)
        with open(transmap_filename(self.lang, "texttags", "xliff"), "w") as outfile:
            outfile.write(str(soup))

    def exportXLSX(self, ignore_alltranslated=False):
        texttags = self._convert_to_json(ignore_alltranslated)
        filename = transmap_filename(self.lang, "texttags", "xlsx")
        to_xlsx(texttags, filename)


class IgnoreFormulaPatternIndexer(object):
    """
    Indexes patterns with only the text as key, replacing all formulas with §formula§
    """
    def __init__(self, lang):
        self.lang = lang
        self.autotrans = RuleAutotranslator()
        self.index = Counter()
        self.untranslated_index = Counter()
        self.translated_index = defaultdict(Counter)
        self._formula_re = re.compile(r"\$[^\$]+\$")
        self._img_re = get_image_regex()
        self._text = get_text_content_regex()
        self._transURLs = {} # Translation URL examples
        # NOTE: Need to run indexer TWO TIMES to get accurate results
        # as the text tags first need to be updated to get an accurate IF index
        self.texttags = read_texttag_index(lang)
        # Ignore specific whitelisted texts which are not translated

    def add(self, engl, translated=None, filename=None):
        normalized_engl = self._formula_re.sub("§formula§", engl)
        normalized_engl = self._img_re.sub("§image§", normalized_engl)
        # Index pattern if it contains TRANSLATABLE text tags ONLY.
        # The translation itself will be perfomed in the autotranslator,
        # while the text tag content itself is indexed in the texttag indexer
        for text_hit in self._text.finditer(engl):
            content = text_hit.group(2).strip()
            if content not in self.texttags: # Untranslatable tag
                return # String not translatable, do not index
        # Count also if translated
        self.index[normalized_engl] += 1
        # Add example link
        # print(filename)
        #"{}#q={}".format(self.translationURLs[filename], to_crowdin_search_string(entry))
        # Track translation for majority selection later
        if translated is not None:
            normalized_trans = self._formula_re.sub("§formula§", translated)
            normalized_trans = self._img_re.sub("§image§", normalized_trans)
            self.translated_index[normalized_engl][normalized_trans] += 1
        else: # untranslated
            self.untranslated_index[normalized_engl] += 1

    def _convert_to_json(self, ignore_alltranslated=False):
        ifpatterns = []
        for (hit, count) in self.index.most_common():
            untransl_count = self.untranslated_index[hit]
            if untransl_count == 0 and ignore_alltranslated:
                continue
            # Get the most common pattern
            transl = "" if len(self.translated_index[hit]) == 0 \
                else self.translated_index[hit].most_common(1)[0][0]
            if count >= 2:  # Ignore non-patterns
                ifpatterns.append({"english": hit,
                    "translated": transl, "count": count,
                    "untranslated_count": untransl_count,
                    "type": "ifpattern"})
        return ifpatterns


    def exportJSON(self, ignore_alltranslated=False):
        ifpatterns = self._convert_to_json(ignore_alltranslated)
        # Export main patterns file
        with open(transmap_filename(self.lang, "ifpatterns"), "w") as outfile:
            json.dump(ifpatterns, outfile, indent=4, sort_keys=True)

        # export file of untranslated patterns
        with open(transmap_filename(self.lang, "ifpatterns.untranslated"), "w") as outfile:
            json.dump(list(filter(lambda p: not p["translated"], ifpatterns)),
                outfile, indent=4, sort_keys=True)

    def exportXLIFF(self, ignore_alltranslated=False):
        ifpatterns = self._convert_to_json(ignore_alltranslated)
        soup = pattern_list_to_xliff(ifpatterns)
        with open(transmap_filename(self.lang, "ifpatterns", "xliff"), "w") as outfile:
            outfile.write(str(soup))

    def exportXLSX(self, ignore_alltranslated=False):
        iftags = self._convert_to_json(ignore_alltranslated)
        filename = transmap_filename(self.lang, "ifpatterns", "xlsx")
        to_xlsx(iftags, filename)


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

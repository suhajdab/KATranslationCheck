#!/usr/bin/env python3
import cffi_re2 as re
from collections import Counter, defaultdict
from ansicolor import red

class CompositeIndexer(object):
    """
    Utility that calls add() once for every child object.
    So you dont need to change indexers all over the place
    """
    def __init__(self, *args):
        self.children = args

    def add(self, *args, **kwargs):
        for child in self.children:
            child.add(*args, **kwargs)

class TextTagIndexer(object):
    def __init__(self):
        self.index = Counter()
        self.translated_index = {}
        self._re = re.compile(r"\\text\{\s*([^\}]+?)\s*\}")

    def add(self, engl, translated=None):
        # Find english hits and possible hits in target lang to be able to match them!
        engl_hits = self._re.findall(engl)
        # Just make sure that transl_hits has the same length as index
        transl_hits = engl if translated is None else self._re.findall(translated)
        if transl_hits:
            print(transl_hits)
        # Find hits in english
        for engl_hit, transl_hit in zip(engl_hits, transl_hits):
            engl_hit = engl_hit.strip()
            transl_hit = transl_hit.strip()
            self.index[engl_hit] += 1
            # If untranslated, do not index translions
            if translated is not None:
                self.translated_index[engl_hit] = transl_hit
        #except Exception as ex:
        #    print(red("Failed to index '{}' --> {}: {}".format(engl, translated, ex) bold=True))

    def exportCSV(self, filename):
        with open(filename, "w") as outfile:
            for (hit, count) in self.index.most_common():
                transl = self.translated_index[hit] if hit in self.translated_index else ""
                outfile.write("\"{}\",\"{}\",{}\n".format(hit, transl, count))


class PatternIndexer(object):
    def __init__(self):
        self.index = defaultdict(list)
        self._re = re.compile(r"\d")

    def add(self, engl, translated):
        # Currently just remove digits
        normalized = self._re.sub("", engl)
        self.index[normalized] += engl

    def exportCSV(self, filename):
        with open(filename, "w") as outfile:
            for (hit, hitlist) in self.index.most_common():
                if len(hitlist) == 1:  # Ignore non-patterns
                    continue
                outfile.write("\"{}\",{}\n".format(hit, len(hitlist)))

if __name__ == "__main__":
    tti = TextTagIndexer()
    source = "john counts $6\\text{balls and }4\\text{orchs and}12\\text{spears}$"
    target = "john räknar $6\\text{bollar och }4\\text{orcher och}12\\text{spjut}$"
    tti.add(source, target)
    print(tti.index)
    print(tti.translated_index)
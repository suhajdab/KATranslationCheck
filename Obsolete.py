

class SimplePatternAutotranslator(object):
    """
    Auto-translates based on simple patterns with known form
    Will mostly auto-translate formula-only etc
    """
    def __init__(self, lang):
        self.lang = lang
        self._contains_text = re.compile(r"\\text\{(?! ?cm\})(?! ?m\})(?! ?g\})(?! ?kg\})(?! ?s\})(?! ?min\})");
        self._re1 = re.compile(r"^(\$[^\$]+\$)\s+(\w+)\s+(\$[^\$]+\$\s*)$")
        self._trans1 = defaultdict(list)
        with open(os.path.join("transmap", lang + ".1.json")) as infile:
            self.transmap1 = json.load(infile)

    def replace_name(self, lang, name):
        """
        Get the localized replacement name
        """
        # TODO not implemented
        return name

    def translate(self, engl):
        m1 = self._re1.match(engl)
        if m1: # $...$ <text> $...$
            # \\text might contain separate translatable text, so ignore
            if self._contains_text.match(engl) is not None:
                return None
            word = m1.group(2)
            if word not in self.transmap1[word]:
                return None # Dont know how to translate
            transWord = self.transmap1[word]
            return engl.replace(word, transWord)



class SimplePatternIndexer(object):
    """
    Indexes simple patterns with known form:
    Tries to find translated forms of given patterns
    """
    def __init__(self, lang):
        self.lang = lang
        self._re1 = re.compile(r"(\$[^\$]+\$)\s+([\w\s]+)\s+(\$[^\$]+\$\s*)")
        self._trans1 = defaultdict(list)

    def add(self, engl, translated=None, filename=None):
        if translated is not None:
            m1e = self._re1.match(engl)
            m1t = self._re1.match(translated)
            if m1e and m1t:
                # Uncomment to debug source of strange patterns.
                #if m1e.group(2) == m1t.group(2):
                #    print("{} ===> {} ({})".format(engl, translated, filename))
                self._trans1[m1e.group(2)].append(m1t.group(2))

    def majority_voted_map(self, src, min_confidence=2):
        return valmap(lambda v: majority_vote(v), src)


    def exportCSV(self):
        with open(os.path.join("transmap", self.lang + ".1.json"), "w") as outfile:
            json.dump(self.majority_voted_map(self._trans1),
                outfile, indent=4, sort_keys=True)

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

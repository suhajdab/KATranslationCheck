

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

#!/usr/bin/env python3
# coding: utf-8
from Rules import *
from ImageAliases import readImageAliases

imageAliases = readImageAliases("177zIAO37SY6xUBUyUE30kn5G_wR7oT-txY8XIN7cecU")

########################
### Initialize rules ###
########################
# Currently hardcoded for DE language
rules = [
    #Wikipedia-listed typos
    TextListRule("Wikipedia-listed typo", "cache/de-typos.txt", severity=Severity.standard),
    #Coordinate separated by comma instead of |
    SimpleRegexRule("Comma in coordinate (| required)", r"\$\(-?\d+([\.,]\d+)?\s*,\s*-?\d+([\.,]\d+)?\)\$", severity=Severity.warning),
    SimpleRegexRule("Semicolon in coordinate (| required)", r"\$\(-?\d+([\.,]\d+)?\s*\;\s*-?\d+([\.,]\d+)?\)\$", severity=Severity.warning),
    SimpleRegexRule("{\ } instead of {\,} inside number", r"\d+\{\\\s+\}\d+", severity=Severity.notice),
    SimpleRegexRule("Simple interval separated by comma instead of semicolon", r"(?<!!)\[\d+\s*,\s*\d+\]", severity=Severity.standard),
    SimpleRegexRule("Must not use {,} inside \\textit in a formula", r"\\textit\{\s*\d+\{,\}\d+\s*\}", severity=Severity.warning),
    SimpleRegexRule("'.* *' needs to be '.**', could cause bad formatting", r"\.\s*\* +\*(?!\*)", severity=Severity.warning),
    IgnoreByMsgidRegexWrapper(r"CC\s+BY-NC-SA\s+\d\.\d",
        SimpleRegexRule("Decimal dot instead of comma inside number (high TPR)", r"\d+\.\d+", severity=Severity.info)),
    SimpleRegexRule("Angle with [RL] prefix", r"\R_\{\d+\^\\circ\}", severity=Severity.warning),
    # Three cases of thin space missing in coordinate
    SimpleRegexRule("Space inserted between **", r"(?<!\*)\* \*(?!\*)", severity=Severity.info),
    SimpleRegexRule("Missing thin space ({\\,}) before or after |-separated coordinate", r"\$?\(\d+([\.,]\d+)?\s*\|\s*\d+([\.,]\d+)?\)\$?", severity=Severity.info),
    #The most simple case of using a decimal point instead
    SimpleRegexRule("Decimal point instead of comma", r"\$-?\s*\d+\.-?\d+\s*\$", severity=Severity.standard),
    SimpleRegexRule("Escaped dollar symbol (€ required, high TPR)", r"(?<!\\\\)\\\\\$", severity=Severity.info),
    SimpleRegexRule("Wrong or missing space between number and € ({\\,} required)", r"\d+( |  |\{,\}|\{\\ \})?€", severity=Severity.info),
    IgnoreByMsgidRegexWrapper(r"^[^\$]+$", # No dollar in string
        SimpleRegexRule("Plain comma used instead of {,}", r"\d+,\d+", severity=Severity.info)),
    #Simple currency value in dollar (matches comma separated and decimal point)
    SimpleRegexRule("Value with embedded dollar symbol", r"\$\s*\\\\?\$\s*\d+([.,]\d+)?\s*\$", severity=Severity.info),
    #Errors in thousands separation
    SimpleRegexRule("Value with multiple or mixed commata or dots", r"(\d+(\.|\{,\})){2,}\d+", severity=Severity.dangerous), #Should be space. Comma without {} ignored.
    DynamicTranslationIdentityRule("Thousands separation via {,} (must be {\\,}) (experimental)", r"(\d+\{,\}\d+\{,\}\d+(\{,\}\d+)*)", negative=True, group=0, severity=Severity.warning), #Should be space. Comma without {} ignored.
    #Dollar not embedded as a symbol 234$ dollar
    SimpleRegexRule("Value suffixed by dollar", r"\d+\$?\s*dollars?", severity=Severity.info),
    SimpleRegexRule("Additional spaces after * for italic word", r"(?<!\*)(?<!^)(?<!\w)\*\s+\w+\s+\*(?!\*)", severity=Severity.info), # Need to avoid hit for *kleiner* oder *größer* etc.
    SimpleRegexRule("Missing thin space before percent (or not escaped correctly) {\\,}\\%", r"(?<!\{\\,\}\\)%\s*\$", severity=Severity.info),
    SimpleRegexRule("Percent symbol in formula not escaped", r"(?<!\\)%\s*\$", severity=Severity.warning),
    SimpleRegexRule("Percent symbol not escaped (high TPR)", r"(?<!\\)%(?!\()", severity=Severity.info),
    SimpleRegexRule("Using {,} instead of {\\,} as thousands separator", r"\d+\{,\}\d\d\d\{,\}\d\d\d", severity=Severity.info),
    SimpleRegexRule("Using {,} instead of {\\,} as thousands separator (high TPR)", r"\d+\{,\}\d\d\d", severity=Severity.notice),
    SimpleRegexRule("Space(s) before thousands separator or comma (use thin space for thousands separators!)", r"\d+(\s+\{,\}|\{,\}\s+|\s+\{,\}\s+)\d", severity=Severity.info),
    SimpleRegexRule("Space(s) before thin space thousands separator", r"\d+(\s+\{\\,\}|\{\\,\}\s+|\s+\{\\,\}\s+)\d", severity=Severity.info),
    # Translator missed english-only world
    SimpleRegexRule("Occurrence of untranslated 'year'", r"(?<!%\()[Yy]ear(?!\)s)", severity=Severity.standard), # These are lookbehind/lookhead assertions ;-)
    SimpleRegexRule("Occurrence of untranslated 'time'", r"\s+[tT]imes?(?![A-Za-z])(?!-[Oo]ut)(?!_\d)", severity=Severity.standard),
    IgnoreByFilenameListWrapper(["de/4_low_priority/about.team.pot"],
            SimpleRegexRule("Occurrence of untranslated 'school'", r"(?<!Old-)(?<!Ivy-League[- ])(?<!High[- ])(?<!Marlborough[- ])(?<!World[- ])\b[S]chool\b", severity=Severity.standard)),
    SimpleRegexRule("Occurrence of untranslated 'not'", r"(?<!\\)(?<!in)\s*\bnot\b", severity=Severity.standard),
    IgnoreByMsgidRegexWrapper(r"What Does the Fox Hear",
        SimpleRegexRule("Occurrence of untranslated 'does", r"(?<!\\)(?<!-)\b[Dd]oesn?\b", severity=Severity.standard)),
    IgnoreByMsgidRegexWrapper(r"What Does the Fox Hear",
        SimpleRegexRule("Occurrence of untranslated 'what", r"\b[WW]hat\b", severity=Severity.standard)),
    SimpleRegexRule("Occurrence of untranslated 'since'", r"\b[Ss]ince\b", severity=Severity.standard),
    IgnoreByMsgidRegexWrapper(r"value: The value to constrain",
        SimpleRegexRule("Occurrence of untranslated 'value'", r"(?<!%\()(?<!Property:)\b[Vv]alues?\b(?!\)s)(?!=)", severity=Severity.standard)),
    IgnoreByFilenameRegexWrapper(r"^de/1_high_priority_platform/_other_.pot$",
        SimpleRegexRule("Occurrence of untranslated 'low(er)'", r"\b[Ll]ow(er)?\b", severity=Severity.standard)),
    IgnoreByMsgidRegexWrapper(r"</?table>",
        SimpleRegexRule("Occurrence of untranslated 'table'", r"(?<!☃ )\b[Tt]able\b", severity=Severity.standard)),
    IgnoreByMsgidRegexWrapper(r"(Ridgemont|Junior|Senior|Riverside)\s+High\b",
        SimpleRegexRule("Occurrence of untranslated 'high(er)'", r"\b[Hh]igh(er)?\b(?!-[Ss]chool)(?! [Ss]chool)(?! Tides)", severity=Severity.info)),
    SimpleRegexRule("Occurrence of untranslated '(counter)clockwise", r"\b([Cc]ounter)?-?[Cc]clockwise\b", severity=Severity.standard),
    IgnoreByMsgidRegexWrapper(r"Attack of the Soft Purple Bunnies",
        SimpleRegexRule("Occurrence of untranslated 'purple' (not as color specifier)", r"(?<!\\)\b[Pp]urple\b(?! Pi)", severity=Severity.standard)),
    SimpleRegexRule("Occurrence of untranslated 'blue' (not as color specifier)", r"(?<!Captain )(?<!\\color\{)(?<!\\)\b[Bb]lue\b", severity=Severity.standard),
    SimpleRegexRule("Standalone untranslated 'of' inside text inside formula", r"\\text\{\s*of\s*\}", severity=Severity.warning),
    SimpleRegexRule("Standalone untranslated 'step' inside text inside formula", r"\\text\{\s*[Ss]tep\s*\d*:?\s*\}", severity=Severity.warning),
    IgnoreByMsgidRegexWrapper(r"Lygia\s+Pape", # red bottles = artwork
        SimpleRegexRule("Occurrence of untranslated 'red' (not as color specifier)", r"(?<!\\)(?<!\\color\{)\b[Rr]ed\b(?! Delicious)(?! Robins)(?! Robbins)", severity=Severity.standard)),
    IgnoreByMsgidRegexWrapper(r"(Summer|Tree|Hour|Art|Lots|System|Museum|Institute|University)\s+of\s+(Drawing|Code|Script(ing)?|Life|Webpage|Databases|Problem|Fun|Higher\s+Education|Art|Technology)",
        IgnoreByMsgidRegexWrapper(r"(University\s+of\s+\w+|Nature of Code|cost of goods sold)", # Any "University of Maryland" etc
            SimpleRegexRule("Occurrence of untranslated 'of'", r"\b[Oo]f\b(?!-)", severity=Severity.info))), #Also allow of inside links etc.
    IgnoreByMsgidRegexWrapper(r"([Gg]reen'?s.+[Tt]heorem|Green Elementary)",
        SimpleRegexRule("Occurrence of untranslated 'green' (not as color specifier)", r"(?<!\\)(?<!Hank )\b[Gg]reen\b", severity=Severity.standard)),
    IgnoreByTcommentRegexWrapper("/measuring-and-converting-money-word-problems", # Ignore for conversion exercises 
        SimpleRegexRule("Occurrence of dollar as string", r"(?<!US-)[Dd]ollars?(?!ville)(?!-Schein)", severity=Severity.notice)), #US-Dollars? & Dollarville allowed
    IgnoreByFilenameRegexWrapper(r"^de/1_high_priority_platform", SimpleRegexRule("'Sie' instead of 'Du'", r"\bSie\b", severity=Severity.notice), invert=True),
    IgnoreByFilenameRegexWrapper(r"^de/1_high_priority_platform", SimpleRegexRule("'Ihre' instead of 'Deine'", r"\bIhre[rms]?\b", severity=Severity.notice), invert=True),
    # Something was translated that must NOT be translated
    SimpleRegexRule("Occurrence of wrongly translated 'Khan Akademie'", r"[Kk]han\s+Akademie", severity=Severity.dangerous),
    SimpleRegexRule("Translated color in command", r"(\\color\{|\\\\)([Bb]lau|[Rr]ot|[Gg]elb|[Gg]rün|[Vv]iolett|[Ll]ila)", severity=Severity.dangerous),
    # Orthographic rules. Generally low severity
    SimpleRegexRule("daß needs to be written as dass", r"\b[Dd]aß\b", severity=Severity.info),
    SimpleRegexRule("Ausreisser needs to be written as Ausreißer", r"\b[Aa]usreisser\b", severity=Severity.info),
    # Recommended translations
    IgnoreByMsgidRegexWrapper(r"TRIANGLES", # Apparently a special code for something in javascript
        TranslationConstraintRule("'Triangle' not translated to 'Dreieck'", r"(?<!\\)triangles?", r"Dreiecke?", severity=Severity.info, flags=re.UNICODE | re.IGNORECASE)),
    # Others
    IgnoreByTcommentRegexWrapper(r"(us-customary-distance|metric-system-tutorial)",
        NegativeTranslationConstraintRule("'mile(s)' translated to 'Meile(n)' instead of 'Kilometer'", r"miles?", r"(?<!\")meilen?", severity=Severity.info, flags=re.UNICODE | re.IGNORECASE)),
    IgnoreByMsgstrRegexWrapper(r"Term", #Ignore false positives if term has any hits
        NegativeTranslationConstraintRule("'term' translated to 'Begriff' instead of 'Term'", r"\bterms?\b", r"\bBegriffe?\b", severity=Severity.standard, flags=re.UNICODE | re.IGNORECASE)),
    NegativeTranslationConstraintRule("'real number' translated to 'reale ...' instead of 'reelle'", r"real\s+numbers?", r"reale", severity=Severity.standard, flags=re.UNICODE | re.IGNORECASE),
    NegativeTranslationConstraintRule("'shaded' translated to 'schraffiert' instead of 'eingefärbt'", r"shaded", r"schraffiert", severity=Severity.standard, flags=re.UNICODE | re.IGNORECASE),
    NegativeTranslationConstraintRule("'shaded' translated to 'schattiert' instead of 'eingefärbt'", r"shaded", r"schattiert", severity=Severity.standard, flags=re.UNICODE | re.IGNORECASE),
    NegativeTranslationConstraintRule("'scientific notation' translated to 'wissenschaftliche Schreibweise' instead of 'Exponentialschreibweise'", r"scientific\s+notation", r"wissenschaftliche\s+schreibweise", severity=Severity.warning, flags=re.UNICODE | re.IGNORECASE),
    NegativeTranslationConstraintRule("'Coach' translated to 'Trainer' instead of 'Coach'", r"coach", r"trainer", severity=Severity.info, flags=re.UNICODE | re.IGNORECASE),
    NegativeTranslationConstraintRule("'Challenge' translated to 'Herausforderung' instead of 'challenge'", r"challenge", r"herausforderung", severity=Severity.info, flags=re.UNICODE | re.IGNORECASE),
    IgnoreByMsgidRegexWrapper(r"[Pp]ost\s*(office|card|alCode|man|-Money)",
        NegativeTranslationConstraintRule("'Post' translated to 'Post' instead of 'Beitrag'", r"\bpost", r"\bpost\b(?!-)", severity=Severity.info, flags=re.UNICODE | re.IGNORECASE)),
    TranslationConstraintRule("'real root(s)' not translated to 'reelle Nullstellen'", r"real\s+roots?", r"reellen?\s+Nullstellen?", severity=Severity.warning, flags=re.UNICODE | re.IGNORECASE),
    TranslationConstraintRule("'complex root(s)' not translated to 'komplexe Nullstellen'", r"complex\s+roots?", r"komplexe Nullstellen?", severity=Severity.warning, flags=re.UNICODE | re.IGNORECASE),
    TranslationConstraintRule("'domain' not translated to 'Definitionsbereich'", r"[Dd]omain", r"Definitions(-|bereich)", severity=Severity.warning, flags=re.UNICODE | re.IGNORECASE),
    TranslationConstraintRule("'DENOMINATOR' not translated to 'DENOMINATOR'", r"DENOMINATOR", r"DENOMINATOR", severity=Severity.warning, flags=re.UNICODE),
    TranslationConstraintRule("'NUMERATOR' not translated to 'NUMERATOR'", r"NUMERATOR", r"NUMERATOR", severity=Severity.warning, flags=re.UNICODE),
    # HTML tags must not be removed. Rules disabled because they don't work.
    #TranslationConstraintRule("'&lt;table&gt;' not translated to '&lt;table&gt;'", r"<table", r"<table", severity=Severity.warning, flags=re.UNICODE),
    #TranslationConstraintRule("'&lt;/table&gt;' not translated to '&lt;/table&gt;'", r"</table", r"</table", severity=Severity.warning, flags=re.UNICODE),
    #TranslationConstraintRule("'&lt;div&gt;' not translated to '&lt;div&gt;'", r"<div", r"<div", severity=Severity.warning, flags=re.UNICODE),
    #TranslationConstraintRule("'&lt;/div&gt;' not translated to '&lt;/div&gt;'", r"</div", r"</div", severity=Severity.warning, flags=re.UNICODE),
    #TranslationConstraintRule("'&lt;span&gt;' not translated to '&lt;span&gt;'", r"<span", r"<span", severity=Severity.warning, flags=re.UNICODE),
    #TranslationConstraintRule("'&lt;/span&gt;' not translated to '&lt;/span&gt;'", r"</span", r"</span", severity=Severity.warning, flags=re.UNICODE),
    # E-Mail must be written exactly "E-Mail". Exceptions: {{email}}, %(error_email), %(email), %(coach_email) %(privacy_email) {{ email }}
    SimpleRegexRule("Wrong syntax of E-Mail", r"(?<!%\()(?<!%\(coach_)(?<!%\(child_)(?<!%\(error_)(?<!%\(privacy_)(?<!\{\{)(?<!\{\{)\s*(eMail|email|Email|EMail|e-Mail|e-mail)s?", severity=Severity.info),
    # Bing issues
    SimpleRegexRule("Space inserted after image URL declaration ('![] (')", r"!\[\]\s+\(", severity=Severity.dangerous),
    SimpleRegexRule("Space inserted before image URL declaration ('! [](')", r"!\s+\[\]\(", severity=Severity.dangerous),
    SimpleRegexRule("Space inserted before & after image URL declaration ('! [] (')", r"!\s+\[\]\s+\(", severity=Severity.dangerous),
    NegativeTranslationConstraintRule("False Bing translation of interactive-graphic", r"☃\s+interactive-graph", r"[Ii]nteraktive\s+Grafik", severity=Severity.dangerous),
    SimpleRegexRule("False Bing translation of Radio", r"☃\s+Radio\b", severity=Severity.dangerous),
    SimpleRegexRule("False Bing translation of input-number", r"[Ee]ingabe-Zahl", severity=Severity.dangerous),
    SimpleRegexRule("False Bing translation of input-number", r"[Ee]ingabe-Nummer", severity=Severity.dangerous),
    SimpleRegexRule("False Bing translation of numeric-input", r"[Nn]umerische[-\s]+Eingabe", severity=Severity.dangerous),
    SimpleRegexRule("False Bing translation of numeric-input", r"[Nn]umerische[-\s]+Eingang", severity=Severity.dangerous),
    SimpleRegexRule("False Bing translation of image", r"☃\s+Bild", severity=Severity.dangerous),
    SimpleRegexRule("Missing translation of **How", r"\*\*[Hh]ow", severity=Severity.dangerous),
    SimpleRegexRule("Missing translation of **What", r"\*\*[Ww]hat", severity=Severity.dangerous),
    SimpleRegexRule("Missing translation of ones", r"\\text\{\s*ones\}\}", severity=Severity.dangerous),
    IgnoreByMsgstrRegexWrapper(r"\d+\^\{\\large\\text\{ten?\}",
        SimpleRegexRule("Missing translation of ten(s)", r"(?<!\d)\^?\{?(\\large)?\\text\{\s*tens?\}\}", severity=Severity.info)),
    SimpleRegexRule("Missing translation of hundred(s)", r"\\text\{\s*hundreds?\}\}", severity=Severity.dangerous),
    # Capitalization
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Dreieck not capitalized", r"\bdreiecke?\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Viereck not capitalized", r"\bvierecke?\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Fünfeck not capitalized", r"\bfünfecke?\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Sechseck not capitalized", r"\bsechsecke?\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Quadrat not capitalized", r"\bquadrate?\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Rechteck not capitalized", r"\brechtecke?\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Kreis not capitalized", r"\bkreise?\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Umfang not capitalized", r"\bumfang\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Fläche not capitalized", r"\bflächen?\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Celsius not capitalized", r"\bcelsius\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Algebra not capitalized", r"\balgebra\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Analysis not capitalized", r"\banalysis\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Textaufgabe not capitalized", r"\btextaufgaben?\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Teiler not capitalized", r"\bteiler\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Addition not capitalized", r"\baddition\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Subtraktion not capitalized", r"\bsubtraktion\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Multiplikation not capitalized", r"\bmultiplikation\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Division not capitalized", r"\bdivision\b", severity=Severity.info)),
    IgnoreByTcommentRegexWrapper(r"SEO\s+keyword",
        SimpleRegexRule("Zahl not capitalized", r"\bzahl\b", severity=Severity.info)),
    # Typos
    SimpleRegexRule("Typo: bliden instead of bilden", r"[Bb]lide[nt]", severity=Severity.info),
    SimpleRegexRule("Typo: bidlen instead of bilden", r"[Bb]idle[nt]", severity=Severity.info),
    SimpleRegexRule("Typo: ähnlich Terme or Ausdrücke instead of ähnliche Terme", r"[Ää]hnlich\s+([Tt]erme?|[Aa]usdr(uck|ücke))", severity=Severity.info),
    SimpleRegexRule("Typo: sit instead of ist", r"\b[Ss]it\b(?!-[Uu]p)", severity=Severity.info),
    SimpleRegexRule("Typo: spielgeln instead of spiegeln", r"[Ss]pielgeln", severity=Severity.info),
    SimpleRegexRule("Typo: zeien instead of zeigen", r"[Zz]eien", severity=Severity.info),
    SimpleRegexRule("Typo: un instead of und", r"\b[Uu]n\b", severity=Severity.info),
    SimpleRegexRule("Typo: dreiek instead of dreieck", r"\b[Dd]reiek\b", severity=Severity.info),
    SimpleRegexRule("Typo: vierek instead of viereck", r"\b[Vv]ierek\b", severity=Severity.info),
    SimpleRegexRule("Typo: fünfek instead of fünfeck", r"\b[Ff]ünfek\b", severity=Severity.info),
    SimpleRegexRule("Typo: sechsek instead of sechseck", r"\b[Ss]echsek\b", severity=Severity.info),
    SimpleRegexRule("Typo: Multiplikaiton instead of Multiplikation", r"\b[Mm]ultiplikaiton\b", severity=Severity.info),
    # Untranslated stuff directly after \n (not machine translated)
    SimpleRegexRule("Untranslated 'First' after \\n", r"\\nFirst", severity=Severity.standard),
    SimpleRegexRule("Untranslated 'Second' after \\n", r"\\nSecond", severity=Severity.standard),
    SimpleRegexRule("Untranslated 'This' after \\n", r"\\nThis", severity=Severity.standard),
    SimpleRegexRule("Untranslated 'That' after \\n", r"\\nThat", severity=Severity.standard),
    # Machine-readable stuff must be identical in the translation
    ExactCopyRule("All image URLs must match in order", r"!\[\]\s*\([^\)]+\)", severity=Severity.warning, aliases=imageAliases),
    ExactCopyRule("All image URLs must match in order (with translation)", r"!\[[^\]](\]\s*\([^\)]+\))", severity=Severity.info, aliases=imageAliases, group=1),
    ExactCopyRule("All GUI elements must match in order", r"\[\[☃\s+[a-z-]+\s*\d*\]\]", severity=Severity.warning),
    DynamicTranslationIdentityRule("Non-identical whitespace before image (auto-translate) (experimental)", r"(\\n(\\n|\s|\*)*!\[)", group=0, severity=Severity.notice),
    # Unsorted stuff
    TranslationConstraintRule("'expression' not translated to 'Term'", r"(?<!polynomial )(?<!quadratic )(?<!☃ )expression", r"term", severity=Severity.notice, flags=re.UNICODE | re.IGNORECASE),
    TranslationConstraintRule("'polynomial expression' not translated to 'Polynom'", r"polynomial expression", r"Polynom", severity=Severity.notice, flags=re.UNICODE | re.IGNORECASE),
]

rule_errors = []


for rule in readRulesFromGDocs("1_I8vBZm9-1NybpIoEEdvAT5m1ehhXXRcILrIljfsUGg"):
    if isinstance(rule, RuleError):
        rule_errors.append(rule)
    else:
        rules.append(rule)

if __name__ == "__main__":
    print("Counting %d rules" % len(rules))

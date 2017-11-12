# Rule types

### SimpleRegexRule

Matches if `Rule string / regex` has any match in the translated string

### SimpleSubstringRule

Like `SimpleRegexRule`, but matches on a substring instead of a Regex.

Usually it should be preferred to use `SimpleRegexRule`.
The only advantage of `SimpleSubstringRule` is that it can be used without escaping special charaters

### TranslationConstraintRule

Matches if `Rule string / regex` matches the **english** version and at the same time `Translated to (regex)` does **NOT** match.

Example: `[Tt]riangle` in *Rule string / regex* and `[Dd]reieck` in *Translated to (regex)* will enforce every instance of *triangle* to be translated as *Dreieck*.

### NegativeTranslationConstraintRule

Like `TranslationConstraintRule`, but matches only if the english regex and the translated regex do NOT match at the same time.

It is easy to create false positives using this rules, therefore only advanced users should use this.

Example: `[Tt]riangle` in *Rule string / regex* and `[Vv]iereck` in *Translated to (regex)* will find any string where *triangle* is translated as *Viereck* (square), but it will have false-positive hits on any translated string where there is ANY other occurrence of *Viereck* while *triangle* occurs in the english string.

### DynamicTranslationIdentityRule

Rarely used rule which hits if the exact hit from `Rule string / regex` (applied to the english string) is found in the translated string.

Can be used to enforce that certain patterns MUST be translated without specifying all possible strings.

There is currently no negated variant of this rule, but its possible to do using Wrappers

Not recommended to use except for the most advanced users. Largely untested.

### SimpleGlobRule

Variant of `SimpleSubstringRule` that uses Globs instead of pure substrings. Internally converted to `SimpleRegexRule`. `*` is converted to `.*`
For syntax details see https://docs.python.org/3.4/library/fnmatch.html#fnmatch.translate

### ExactCopyRule

Generates a list of hits in the english strings and generates a hit if the list of regex hits in the english string is not identical to the list of regex hits in the translated string.

Usually generates false positives if languages require reordering formulas or images.

Mostly this rule is used in orer to provide.

There is the possibility of providing an alias map which allows to ignore certain english -> translated mismatches. This is currently not possible on the spreadsheet ruleset but is used in Python to manually allow translated images (which have a different URL) by creating a spreadsheet containing `english URL, translated URL` mappings.

Example 1: All image URLs should be the same (and in the same order)
Example 2: All digits should be the same (and in the same order)

### TextListRule

A rule that excepts a text list of words (e.g. typos), each of which will generate a rule hit. The file is expected to contain one string per line.
If the file does not exist, this method prints a red bold error message and does not
generate any rule hits.

Not available in spreadsheets as it requires a file. A common usecase is to parse the wikipedia list of common typos.

### AutoUntranslatedRule

Give this rule a comma-separated list of strings which must ALWAYS be translated. Will hit any untranslated instance of those strings. The first character of each word is handled in a case-insensitive way. Internally converted to a `SimpleRegexRule`.

### AutoTranslationConstraintRule

Like `TranslationConstraintRule`, but automatically handles the first character as case-insensitive.

# Rule wrappers and logic

Note that rule wrappers and logic can be nested and combined using logic without restrictions.

### IgnoreByFilenameRegexWrapper(filename_regex, rule, invert=False)

Rule wrapper that ignores the rule for a specific set of files (PO/XLIFF files) that match `filename_regex`. Usually used to ignore computer science stuff because it contains HTML

### IgnoreByFilenameListWrapper(filenames, rule)

Like `IgnoreByFilenameRegexWrapper` but takes a list of filenames instead of a regex.

### IgnoreByMsgidRegexWrapper(msgid_regex, rule)

Rule wrapper that ignores any string whose english version matches `msgid_regex`.

### IgnoreByMsgstrRegexWrapper(msgstr_regex, rule)

Rule wrapper that ignores any string whose translated version matches `msgstr_regex`.

### IgnoreByTcommentRegexWrapper(comment_regex, rule)

Rule wrapper that ignores any string whose comment matches `comment_regex`.

Currently does not work because of XLIFF processing not parsing comments properly.




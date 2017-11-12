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


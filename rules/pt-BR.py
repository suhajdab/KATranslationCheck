#!/usr/bin/env python3
# coding: utf-8
from Rules import *
from ImageAliases import readImageAliases

########################
### Initialize rules ###
########################
# Currently hardcoded for DE language
rules = []
rule_errors = []


for rule in readRulesFromGDocs("1EF8dFohJFWMhyncngqqeX29xcnGQdySAZaa6Ou0QuHY"):
    if isinstance(rule, RuleError):
        rule_errors.append(rule)
    else:
        rules.append(rule)

if __name__ == "__main__":
    print("Counting %d rules" % len(rules))
    for ruleError in rule_errors:
        print(ruleError.msg)

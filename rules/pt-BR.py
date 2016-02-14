#!/usr/bin/env python3
# coding: utf-8
from Rules import *
from ImageAliases import readImageAliases

rules, rule_errors = readRulesFromGoogleDocs("1EF8dFohJFWMhyncngqqeX29xcnGQdySAZaa6Ou0QuHY")

if __name__ == "__main__":
    print("Counting %d rules" % len(rules))
    for ruleError in rule_errors:
        print(ruleError.msg)

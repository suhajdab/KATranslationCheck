#!/usr/bin/env python3
# coding: utf-8
from Rules import *
from ImageAliases import readImageAliases


rules, rule_errors = readRulesFromGoogleDocs("1Jmt2Uyo_rTLaiCO5C253nVQom9LuJr3rPYtZYDwe2c0")

rule_errors = []

if __name__ == "__main__":
    print("Counting %d rules" % len(rules))

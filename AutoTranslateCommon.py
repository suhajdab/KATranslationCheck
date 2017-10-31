#!/usr/bin/env python3
import re

def get_text_regex():
    exceptions = ["cm", "m", "g", "kg", "s", "min", "max", "h", "cm"]
    exc_clause = "".join([r"(?! ?" + ex + r"\})" for ex in exceptions])
    regex = r"(\\(text|mathrm)\s*\{" + exc_clause + r")"
    console.llog(regex)
    return re.compile(regex)


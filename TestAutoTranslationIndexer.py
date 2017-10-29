#!/usr/bin/env python3
from AutoTranslationTranslator import *
from ansicolor import red

def assertSame(engl):
    trans = RuleAutotranslator()
    result = trans.translate(engl)
    if result != engl:
        print(red("Failed to autotranslate '{}'".format(engl), bold=True))

def assertNotTranslated(engl):
    trans = RuleAutotranslator()
    result = trans.translate(engl)
    if result is not None:
        print(red("String should not be translated:'{}'".format(engl), bold=True))

if __name__ == "__main__":
    # Artificial strings
    assertSame("$a$")
    assertSame(">$a$")
    assertNotTranslated("$i$q")
    assertSame(" $b$ ")
    assertSame("$c$\\n")
    assertSame("$d$\\n\\n$db$ \\n")

    assertNotTranslated("$d\\\\text{foo}$")
    assertSame("$d\\\\text{ cm}$")
    assertSame("$d\\\\text{ g}$")
    assertSame("$d\\\\text{ m}$")
    assertSame("$d\\\\text{cm}$")
    assertSame("$d\\\\text{g}$")
    assertSame("$d\\\\text{m}$")

    # Real strings
    assertSame("web+graphie://ka-perseus-graphie.s3.amazonaws.com/b8ca00d508c9e7b593c669977fdde31570195273")
    assertSame("https://ka-perseus-images.s3.amazonaws.com/b8ca00d508c9e7b593c669977fdde31570195273.svg")
    assertSame("![](https://ka-perseus-images.s3.amazonaws.com/b8ca00d508c9e7b593c669977fdde31570195273.svg)")
    assertSame("https://ka-perseus-images.s3.amazonaws.com/b8ca00d508c9e7b593c669977fdde31570195273.png")
    assertSame("$\\\\blue{A_c} = \\\\pi (\\\\pink{10})^2$\\n\\n $\\\\blue{A_c} = 100\\\\pi$\\n\\n ![](web+graphie://ka-perseus-graphie.s3.amazonaws.com/b8ca00d508c9e7b593c669977fdde31570195273)")
    assertSame(">$\\\\pink{\\\\text{m}\\\\angle D} + \\\\blue{106} = 180$")
    assertSame("$3c^3-12c-8$")

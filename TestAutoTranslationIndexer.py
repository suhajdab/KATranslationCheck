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

def assertNameTrans(engl, exp):
    trans = NameAutotranslator("sv-SE")
    result = trans.translate(engl)
    if result != exp:
        print(red("'{}' translated as '{}'".format(engl, result), bold=True))

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
    assertSame("$d\\\\text{ cm}$")
    assertSame("$d\\\\text{ g}$")
    assertSame("$d\\\\text{ m}$")
    assertSame("$d\\\\text{cm}$")
    assertSame("$d\\\\text{g}$")
    assertSame("$d\\\\text{m}$")
    assertSame("$d\\\\text{ s}$")
    assertSame("$d\\\\text{ min}$")
    assertNotTranslated("$d\\\\text{ sa}$")
    assertNotTranslated("$d\\\\text{ max}$")

    # Real strings
    assertSame("web+graphie://ka-perseus-graphie.s3.amazonaws.com/b8ca00d508c9e7b593c669977fdde31570195273")
    assertSame("https://ka-perseus-images.s3.amazonaws.com/b8ca00d508c9e7b593c669977fdde31570195273.svg")
    assertSame("![](https://ka-perseus-images.s3.amazonaws.com/b8ca00d508c9e7b593c669977fdde31570195273.svg)")
    assertSame("https://ka-perseus-images.s3.amazonaws.com/b8ca00d508c9e7b593c669977fdde31570195273.png")
    assertSame("$\\\\blue{A_c} = \\\\pi (\\\\pink{10})^2$\\n\\n $\\\\blue{A_c} = 100\\\\pi$\\n\\n ![](web+graphie://ka-perseus-graphie.s3.amazonaws.com/b8ca00d508c9e7b593c669977fdde31570195273)")
    assertSame(">$\\\\pink{\\\\text{m}\\\\angle D} + \\\\blue{106} = 180$")
    assertSame("$3c^3-12c-8$")
    assertSame("### $\\log_{\\,5}{25}$ = [[☃ numeric-input 1]]")
    assertSame("(-2,4]")
    assertSame("[-2,4)")
    assertSame("[-2,-4]")
    assertSame("$\\\\begin{align}\\n&F(x)=4x^2-5x\\n\\\\\\\\\\\\\\\\\\n&f(x)=F'(x)\\n\\\\end{align}$\\n\\n$\\\\displaystyle\\\\int_1^4 f(x)\\\\,dx=$ [[☃ numeric-input 1]]")
    assertSame("$\\\\displaystyle\\\\sum_{j=0}^3 3-jn=\\\\,?$\\n\\n[[☃ radio 1]]")
    assertSame("$\\\\displaystyle\\\\int x^{-7}\\\\,dx=$ [[☃ expression 1]]$+C$")
    assertSame("$\\\\text{cm}/\\\\text{min}$")
    assertSame("$\\\\text{cm}^2/\\\\text{h}$")
    assertSame("$\\\\begin{align}\\nf(x)&=\\\\sin(-3x^2-3x+7)\\n\\\\\\\\\\\\\\\\\\nf'(x)&=\\\\,?\\n\\\\end{align}$\\n\\n[[☃ radio 1]]")
    assertSame("$2x^2-x+5$")
    assertSame("$f(x)=x^2$\\n\\n$f'(x)=$ [[☃ expression 1]]")
    assertSame("$\\\\dfrac{d}{dx}\\\\left[\\\\dfrac{x^3}{\\\\sin(x)}\\\\right]=$ [[☃ expression 1]]\\n")
    assertSame("$\\\\displaystyle\\\\lim_{x\\\\to \\\\frac{\\\\pi}{4}}\\\\csc(x)=?$\\n\\n[[☃ radio 1]]")
    
    assertSame("$y=\\\\arcsin\\\\!\\\\left(\\\\dfrac{x}{4}\\\\right)$\\n\\n$\\\\dfrac{dy}{dx}=?$\\n\\n[[☃ radio 1]]")
    
    
    
   
    
    #B | $x$ |$-2$ | $-1.5$ | $-1.25$ | $-1.1$ | $-1.005$ | $-1.001$ \n:- | -: | :-: | :-: | :-: | :-: | :-: | :-:\n| $g(x)$ | $-2.91$ | $-2.5$ | $-2.2$ | $-1.99$ | $-1.86$ | $-1.86$

    # Name translation
    assertNameTrans("Only John", "Endast John")
    assertNameTrans("Only Jack", "Endast Jack")
    assertNameTrans("Only John.", "Endast John.")

    assertNameTrans("Neither John nor Jack", "Varken John eller Jack")
    assertNameTrans("Neither Jack nor John.", "Varken Jack eller John.")

    assertNameTrans("Either John or Jack", "Antingen John eller Jack")
    assertNameTrans("Either Jack or John.", "Antingen Jack eller John.")

    assertNameTrans("Both John and Jack", "Både John och Jack")
    assertNameTrans("Both Jack and John.", "Både Jack och John.")

    assertNameTrans("Neither John nor Jack are correct", "Varken John eller Jack har rätt")
    assertNameTrans("Neither Jack nor John are correct.", "Varken Jack eller John har rätt.")

    assertNameTrans("Both John and Jack are correct", "Både John och Jack har rätt")
    assertNameTrans("Both Jack and John are correct.", "Både Jack och John har rätt.")

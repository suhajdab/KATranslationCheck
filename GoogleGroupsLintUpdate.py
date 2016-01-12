#!/usr/bin/env python3
from selenium import webdriver
from lxml.html import fromstring

def fetchSeleniumFF(url):
    browser = webdriver.Firefox()
    browser.set_window_size(1920, 1080)
    browser.get(url)
    time.sleep(2)
    page_source = browser.page_source
    browser.quit()
    return page_source

def getLatestLintPostURLForLanguage(lang="de"):
    """
    Get the latest lint result URL from google groups for a given language.
    Returns the URL to a Google Groups post.
    """
    page_source = fetchSeleniumFF("https://groups.google.com/a/khanacademy.org/forum/#!forum/i18n-reports")
    frontpage = fromstring(page_source)
    frontpage.make_links_absolute("https://groups.google.com/a/khanacademy.org/forum")
    elements = frontpage.xpath('//a[@class="IVILX2C-p-Q"]') # WTF is this string?
    #with open("out.html","w") as outf:
    #    outf.write(page_source)
    for element in elements:
        txt = element.text
        if txt.endswith("crowdin entries linted for {0}".format(lang)):
            return (element.get("href"))

def getLatestLintDownloadLink(lang="de"):
    page_source = fetchSeleniumFF(getLatestLintPostURLForLanguage(lang))
    frontpage = fromstring(page_source)
    elements = frontpage.xpath('//a[@class="gwt-Anchor"]') # WTF is this string?
    # Return only last link
    latest = None
    for element in elements:
        txt = element.text
        if txt == "Herunterladen":
            latest = element.get("href")
    if latest is None:
        raise NoResultException()
    return latest

def updateLintFromGoogleGroups(lang="de"):
    url = getLatestLintDownloadLink()
    response = requests.get(url)
    filename = os.path.join("cache", "{0}-lint.csv".format(lang))
    with open(filename, "w") as outfile:
        outfile.write(response.text)
    print(black("Updated %s" % filename, bold=True))
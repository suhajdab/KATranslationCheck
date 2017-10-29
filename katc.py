#!/usr/bin/env python3
from UpdateAllFiles import updateTranslations
from check import performRender, performRenderLint
from IMAPLint import updateLintIMAPHandler
from VideoTranslations import updateVideoMap
from PolyglottIndexer import buildPolyglottIndex
from XLIFFReader import autotranslate_xliffs

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="Commands")
    # Generic argument
    parser.add_argument('-l', '--language', default="de", help='The language directory to use/extract (e.g. de, es)')

    updateTranslationsCmd = subparsers.add_parser('update-translations')
    updateTranslationsCmd.add_argument('-j', '--num-processes', default=16, type=int, help='Number of processes to use for parallel download')
    updateTranslationsCmd.add_argument('-f', '--force-filemap-update', action="store_true", help='Force updating the filemap')
    updateTranslationsCmd.add_argument('-a', '--all-languages', action="store_true", help='Download all languages')
    updateTranslationsCmd.add_argument('-x', '--xliff', action="store_true", help='Download as XLIFF')
    updateTranslationsCmd.set_defaults(func=updateTranslations)

    updateLint = subparsers.add_parser('update-lint')
    updateLint.set_defaults(func=updateLintIMAPHandler)

    autotranslate = subparsers.add_parser('autotranslate')
    autotranslate.add_argument('-j', '--num-processes', default=16, type=int, help='Number of threads to use for parallel processing')
    autotranslate.add_argument('-u', '--upload', action="store_true", help='Upload to Crowdin')
    autotranslate.add_argument('-a', '--approve', action="store_true", help='For --upload, auto-approve the strings')
    autotranslate.add_argument('-f', '--filter', default="", help='Ignore file paths that do not contain this string, e.g. exercises or 2_high_priority')
    autotranslate.add_argument('-p', '--patterns', action="store_true", help='Recognize and export patterns. Will consume a lot of RAM.')
    autotranslate.set_defaults(func=autotranslate_xliffs)

    renderLint = subparsers.add_parser('update-video-translations')
    renderLint.set_defaults(func=updateVideoMap)

    render = subparsers.add_parser('render')
    render.add_argument('-d', '--download', action='store_true', help='Download or update the directory')
    render.add_argument('--only-lint', action='store_true', help='Only render the lint hierarchy')
    render.add_argument('--no-lint', action='store_true', help='Do not render the lint hierarchy')
    render.add_argument('outdir', nargs='?', default=None, help='The output directory to use (default: output-<lang>)')
    render.set_defaults(func=performRender)

    render = subparsers.add_parser('index')
    render.add_argument('-t', '--table', type=int, default=1, help='Table offset (where to store the data in YakDB. 1 => production setup)')
    render.set_defaults(func=buildPolyglottIndex)

    args = parser.parse_args()

    # Call args.func, but do not catch AttributeError inside args.func()
    try:
        args.func
        err = False
    except AttributeError:
        parser.print_help()
        err = True
    if not err:
        args.func(args)

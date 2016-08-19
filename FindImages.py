#!/usr/bin/env python3
import argparse
import os.path
import json
from check import readPOFiles
import cffi_re2 as re2
import simplejson as json

imageRegex = re2.compile(r"https?://ka-perseus-images\.s3\.amazonaws.com/([a-z0-9]+)\.(jpeg|jpg|png)")
graphieRegex = re2.compile(r"web+graphie://ka-perseus-graphie\.s3\.amazonaws.com/([a-z0-9]+)")

images = []
graphie = []

def findInPO(po):
    for entry in po:
        engl = entry.msgid
        trans = entry.msgstr

        for hit in imageRegex.findall(engl) + graphieRegex.findall(trans):
            images.append("{}.{}".format(hit[0], hit[1]))

        for hit in graphieRegex.findall(engl) + graphieRegex.findall(trans):
            graphie.append(hit[0])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--language', default="de", help='The language to use')
    args = parser.parse_args()

    po = readPOFiles(os.path.join("cache", args.language))
    for pot in po.values():
        findInPO(pot)

    with open(os.path.join("output", args.language, "images.json"), "w") as outfile:
        json.dump(images, outfile)

    with open(os.path.join("output", args.language, "graphie.json"), "w") as outfile:
        json.dump(graphie, outfile)

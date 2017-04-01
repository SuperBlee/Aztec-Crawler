# -*- coding: utf-8 -*-

try:
    import ujson as json
except:
    import json

import sys


def getDictInfo(d):
    retKey, retItem = None, []
    for key, item in d.iteritems():
        retKey, retItem = key, item
    return retKey, retItem


if __name__ == "__main__":
    dictFile = "results/vocabs.txt"
    if dictFile is "":
        sys.exit("Please Indicate File Path")

    try:
        f = open(dictFile, "r")
    except IOError as e:
        sys.exit("IO Error {0}, {1}".format(e.errno, e.strerror))
    except:
        sys.exit("Unexpected Error")

    data = f.readlines()
    dataBuffer = []

    for dataLine in data:
        dataLineLoad = json.loads(dataLine)

        # Use following function to get the word and its synonym
        getDictInfo(dataLineLoad)

        # Or directly use this buffer
        dataBuffer.append(dataLineLoad)


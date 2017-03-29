"""
This is the file to generate the Aztec Medical Dictionary.
First Catch a ID list from "http://bioportal.bioontology.org/ontologies/MESH/?p=classes&conceptid=http%3A%2F%2Fpurl.bioontology.org%2Fontology%2FMESH%2FD000602"
Then in each ID, fetch the word and then recursively go into its child.
"""

import urllib2
import requests

def parseID(url):
    """
    From the content page, extract all the sub-urls of all the labels as the starts of recursions.
    :param url: The URL of the content page
    :return: The list of all starting labels, and list of top-layer variable names
    """

    urlList, medWordList = [], []

    response = urllib2.urlopen(url)
    pageSource = response.read()

    r = requests.get(url= url)
    # pageSource = r.text

    print pageSource
    print len(pageSource)
    return urlList, medWordList

if __name__ == "__main__":

    parseID(url= contentURL)

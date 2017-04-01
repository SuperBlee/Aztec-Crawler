# -*- coding: utf-8 -*-

"""
This is the file to generate the Aztec Medical Dictionary.
First Catch a ID list from "http://bioportal.bioontology.org/ontologies/MESH/?p=classes&conceptid=http%3A%2F%2Fpurl.bioontology.org%2Fontology%2FMESH%2FD000602"
Then in each ID, fetch the word and then recursively go into its child.
"""

from bs4 import BeautifulSoup
import requests
import ujson as json
import time
import os
import logging

APIKEY = "apikey=80a85487-ab74-4a87-9ad2-5c1255962a76"

def parseID(file):
    """
    Extract urls from the file
    :param file: from with to extract urls and labels
    :return: urlList to start recursion and top layer words
    """

    # The information we are interested in locates in each tag <a> with "class"=="text"
    # Sub-url is in the "id" field of tag <a>
    # The vocabulary is in the <span> tag
    urlList, medWordList = [], []
    soup = BeautifulSoup(open(file), "html.parser")
    urlTags = soup.find_all('a')
    for urlTag in urlTags:
        if u'class' in urlTag.attrs and urlTag['class'][0] == 'text':
            spanSoup = BeautifulSoup(str(urlTag), 'lxml')
            spanTag = spanSoup.find_all("span")
            if len(spanTag) != 0:
                urlList.append(urlTag['id'])
                medWordList.append(spanTag[0].string)
    return urlList, medWordList

def fetchChildrenInfo(url):
    """
    Fetch Children's Information, which includes synonyms, names, and children's urls.
    :param url: The url of a "self" page
    :return: 3 lists - synonym, names, URLs of children
    """
    synonym, URLs = [], []
    name = None

    time.sleep(0.1)
    r = requests.get(url+"?"+APIKEY)
    # print r.text
    jsonDict = json.loads(r.text)

    if 'synonym' in jsonDict:
        synonym = jsonDict['synonym']
    if 'prefLabel' in jsonDict:
        name = jsonDict['prefLabel']


    jLinksDict = jsonDict['links']
    if 'children' in jLinksDict:
        time.sleep(0.1)
        rChild = requests.get(jLinksDict['children']+"?"+APIKEY)
        jChildDict = json.loads(rChild.text)
        childPageCount = jChildDict['pageCount']
        if childPageCount > 1:
            childPageList = ["page={}".format(i) for i in xrange(1,childPageCount+1)]
        else:
            childPageList=["page=1"]

        for childPageNum in childPageList:
            childURL = url + "/children?"+childPageNum
            URLs += parseChildPage(url=childURL)
    return name, synonym, URLs

def parseChildPage(url):
    time.sleep(0.1)
    r = requests.get(url+"&"+APIKEY)
    # print r.text
    jsonDict = json.loads(r.text)
    collectionList = jsonDict['collection']
    return [collectionItem['links']['self'] for collectionItem in collectionList]

if __name__ == "__main__":

    sourceFile = "source.html"
    urlList, medWords = parseID(file=sourceFile)

    """
    Now we do the recursion:
        Step 1: Find the children link;
        Step 2: Add to the urlList;
        Step: Move to next entry of the urlList and Go to Step 1;
    """

    curIndex = 0

    prefixURL = "http://data.bioontology.org/ontologies/MESH/classes/"
    urlList = [prefixURL + subURL for subURL in urlList]

    newMedWords = []
    newSynonym = []
    os.remove("results/vocabs.txt")
    os.remove("results/syn.txt")
    with open("results/vocabs.txt", "w") as vocabFile, \
            open("results/syn.txt", "w") as synFile, \
            open("Exception.txt", "w") as exp:
        while curIndex < len(urlList):
            try:
                # Get the current sub-url
                curURL  = urlList[curIndex]

                childrenWords, childSyns, childrenURLs = fetchChildrenInfo(curURL) # Fetch all the children's name and url

                urlList = urlList + childrenURLs # Concatenate the lists

                # newMedWords.append(childrenWords)
                # newSynonym += childSyn

                if childrenWords is not None:
                    # vocabFile.write(str(curIndex)+childrenWords+"\n")
                    # if len(childSyns) != 0:
                        # synFile.write(str(curIndex)+"\n")
                        # for childSyn in childSyns:
                          #  synFile.write(childSyn+"\n")
                    childDict = {childrenWords : childSyns}
                    vocabFile.write(json.dumps(childDict)+"\n")

                if curIndex%50 == 0:
                    print "Now at index # {}, {} in total.".format(str(curIndex), str(len(urlList)))
                curIndex += 1  # Update the curIndex
            except:
                exp.write("Other Errors\n")
                curIndex += 1




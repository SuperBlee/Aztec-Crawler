# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import time
import os
import sys
from nltk.stem import WordNetLemmatizer

try:
    import ujson as json
except:
    import json

"""
This is the file to generate the Aztec Medical Dictionary.
First Catch a ID list from "http://bioportal.bioontology.org/ontologies/MESH/?p=classes&conceptid=http%3A%2F%2Fpurl.bioontology.org%2Fontology%2FMESH%2FD000602"
Then in each ID, fetch the word and then recursively go into its child.
"""

API_KEY = "apikey=80a85487-ab74-4a87-9ad2-5c1255962a76"
PREFIX_URL = "http://data.bioontology.org/ontologies/MESH/classes/"

RAW_DATA = "data/source.html"
DATA = "data/top_entry.txt"


def judge_text(text):
    return False if text == "ajax_class" else True


def parse_id(in_file):
    """
    Extract urls from the file
    :param in_file: from with to extract urls and labels
    """

    # The information we are interested in locates in each tag <a></a>
    # with "class"=="text". Sub-url is in the "id" field of tag <a></a>
    soup = BeautifulSoup(open(in_file), "html.parser")
    url_tags = soup.find_all('a', class_="text", text=judge_text)
    with open(DATA, "w") as fout:
        for url_tag in url_tags:
            fout.write(url_tag['id'] + "\n")


def fetch_children_url(source_dict, hrc):
    """
    Fetch children's urls.
    :param source_dict: The url of a "self" page.
    :return: list - URLs of children
    """
    URLs = []

    # Get the term links: may contain "children" or may not
    links = source_dict['links']
    self_url = links['self']

    if 'children' in links:
        time.sleep(0.1)
        child_page = requests.get(links['children'] + "?" + API_KEY)
        child_page_info = json.loads(child_page.text)
        child_page_count = child_page_info['pageCount']

        # Append the URLs from the 1st child
        if 'collection' in child_page_info:
            URLs += mine_self_from_child(source_dict=child_page_info, hrc=hrc)

        # Append the URLs from other children if exist
        if child_page_count > 1:
            for sibling_child_page_num in ["page={}".format(i) for i in xrange(2, child_page_count + 1)]:
                child_url = self_url + "/children?" + sibling_child_page_num + "&" + API_KEY
                r = requests.get(child_url)
                sibling_page_info = json.loads(r.text)
                URLs += mine_self_from_child(sibling_page_info, hrc=hrc)
    return URLs


def parse_words(source_dict):
    """
    Extract the synonym and the prefLabel from a given dictionary
    :param source_dict: the original dictionary from which we extract the information
    :return: the name of the term and the list of the synonyms
    """
    name, syn = None, []
    if 'synonym' in source_dict:
        syn = source_dict['synonym']
    if 'prefLabel' in source_dict:
        name = source_dict['prefLabel']
    return name, syn


def mine_self_from_child(source_dict, hrc):
    # Extract the "self" label from the source_dict
    # Add the hrc in each tuple
    collection_list = source_dict['collection']
    return [(item['links']['self'], hrc) for item in collection_list]


def main():
    """
    Need to be renamed.
    :return: write the voabs, syns, exceptions
    """

    # Remove the files if existing before creating new ones
    OUT_VOCAB = "results/vocabs.txt"
    OUT_SYN = "results/syn.txt"
    OUT_EXCP = "results/exception.txt"
    for f in [OUT_SYN, OUT_VOCAB, OUT_EXCP]:
        if os.path.isfile(f):
            os.remove(f)

    """
    Now we do the recursion:
        Step 1: Find the children link;
        Step 2: Add to the url_list;
        Step: Move to next entry of the url_list and Go to Step 1;
    """
    with open(DATA, "r") as fin:
        url_list = fin.readlines()

    # Write down the urls as tuples, 0 as the first level
    url_list = [((PREFIX_URL + subURL).strip(), 0) for subURL in url_list]

    with open(OUT_VOCAB, "w") as vocab_file, \
            open(OUT_SYN, "w") as syn_file, \
            open(OUT_EXCP, "w") as exp_file:
        cur_index = 0
        while cur_index < len(url_list):
            # Current url of the term, current level number (hierarchy) of the term
            cur_url, cur_hrc = url_list[cur_index]
            try:
                # Get the current sub-url
                time.sleep(0.1)
                r = requests.get(cur_url + "?" + API_KEY)
                source_dict = json.loads(r.text)

                # Getting the vocabulary and the synonym from this page.
                vocab, syn = parse_words(source_dict=source_dict)
                if cur_hrc + 1 < int(level):
                    # Fetch all the children's name and url
                    children_urls = fetch_children_url(source_dict=source_dict, hrc=cur_hrc + 1)
                    # print children_urls
                    url_list = url_list + children_urls  # Concatenate the lists

                if vocab is not None:
                    syn_file.write(json.dumps({vocab: syn}) + "\n")
                    vocab_file.write(vocab + "\n")

                if cur_index % 100 == 0:
                    print "\tNow at index # {}, {} in total.".format(str(cur_index), str(len(url_list)))
            except UnicodeEncodeError as unicode_err:
                exp_file.write(str(unicode_err))
            except KeyError as key_err:
                exp_file.write(str(key_err))
            except:
                pass
            cur_index += 1


def extract_vocab():
    # Give the input and the output
    IN_VOCAB = "results/vocabs.txt"
    OUT_WORDS = "results/onto.txt"

    # Declare the lemmatizer
    lmtz = WordNetLemmatizer()

    words_set = set()
    with open(IN_VOCAB, "r") as in_file:
        lines = in_file.readlines()
        for line in lines:
            # remove comma
            words = line.strip().replace(",", "").lower().split(" ")
            for word in words:
                word = lmtz.lemmatize(word)  # remove the plural
                words_set.add(word)

    with open(OUT_WORDS, "w") as out_file:
        words_set = list(words_set)
        for word in words_set:
            out_file.write(word + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 1 + 1:
        print "Usage python %s <number of level>" % sys.argv[0]

    print "Extraction of dictionary from \"data.bioontology.org\"!"

    level = sys.argv[1]

    print "You are extracting the words from level %s" % level

    if not os.path.isfile(DATA):
        parse_id(RAW_DATA)

    print "Extracting the phrases and synonyms..."
    main()
    print "Extracting all the single words..."
    extract_vocab()

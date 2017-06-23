Aztec Crawler
===

Author: Zeyu Li
Date: May-31-2017 (Cesar Chavez Day)

## Introduction
#### Aztec
You may have heard of Aztec! If not, please check it our anytime [here](https://www.aztec.bio)

#### What's in this repo
It downloads the medical-related vocabularies from [here](http://bioportal.bioontology.org/ontologies/MESH/?p=classes&conceptid=http%3A%2F%2Fpurl.bioontology.org%2Fontology%2FMESH%2FD000602).

## Usage
Just do
```
python main.py <number of level>
```
and it can generate out put in `results/vocabs.txt` and `results/syn.txt`.
The `vocabs.txt` is a file of all vocabulary and `syn.txt` gives the __word - synonyms__ relations.
The `onto.txt` gives all the single lemmatized words in `vocabs.txt`.

Please use `load.py` to load the result.

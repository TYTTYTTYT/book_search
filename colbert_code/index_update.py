#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, getopt
import json
import csv
import os
import sys

from colbert.infra import Run, RunConfig, ColBERTConfig
from colbert.data import Queries, Collection
from colbert import Indexer, Searcher


checkpointp = 'ColBERT/docs/downloads/colbertv2.0'
index_name = 'colbertv2.0'
collection = 'collection.tsv'


def getvalue(argv):

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>\n')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            print('inputfile: json file')
            print('outputfile: tsv file')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    return inputfile, outputfile

def jsontotsv(inputfile):
    with open(inputfile, "r", encoding="utf-8") as f:
        lines = f.readlines()

    question = []
    label = []
    passage_id = []
    n = 0

    for line in lines:
        i = json.loads(line.strip("\n"))
        i["description"] = i["description"].replace("\n", " ")
        # convert author list to string
        a = " ".join(i["author_list"])
        a = a.replace("\n", " ")

        # print(i["author_list"])
        # question.append(i["title"] + ". " + i["description"] + "" + i["author_list"])
        question.append(i["title"] + ". " + i["description"] + "" + a  + ".")
        label.append(n)
        passage_id.append(i["book_id"])
        n = n + 1

    with open('collection.tsv', 'w', encoding="utf-8") as f:
        tsv_w = csv.writer(f, delimiter='\t', lineterminator='\n')
        # tsv_w.writerow(['label', 'question'])
        for num in range(len(lines)):
            tsv_w.writerow([label[num], question[num]])

def indexer(checkpointp, index_name, collection):
    nbits = 2   # encode each dimension with 2 bits
    doc_maxlen = 300   # truncate passages at 300 tokens
    collection = os.path.join(collection)
    collection = Collection(path=collection)
    checkpoint = checkpointp
    index_name = f'{index_name}.{nbits}bits'


    with Run().context(RunConfig(nranks=1, experiment='notebook')):  # nranks specifies the number of GPUs to use.
        config = ColBERTConfig(doc_maxlen=doc_maxlen, nbits=nbits)

        indexer = Indexer(checkpoint=checkpoint, config=config)
        indexer.index(name=index_name, collection=collection, overwrite=True)

if __name__ == "__main__":
    inputfile, outputfile = getvalue(sys.argv[1:])
    jsontotsv(inputfile)
    indexer(checkpointp, index_name, collection)
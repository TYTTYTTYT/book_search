#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, getopt
import json
import csv
import os
import sys

# ColBERT root path
sys.path.insert(0, '/home/adqaicp/documents/ColBERT')

# ColBERT imports
from colbert.infra import Run, RunConfig, ColBERTConfig
from colbert.data import Queries, Collection
from colbert import Indexer, Searcher

# Define the path before running the code
checkpointp = '/home/adqaicp/documents/ColBERT/docs/downloads/colbertv2.0'
index_name = 'colbertv2.0'


def getvalue(argv):

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('-i <inputfile> -o <index-output-path>\n or -h for help')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('\n------ help ------\n-i <inputfile> -o <index-output-path>\n')
            print('<inputfile>: \njson file ->> example: test.json\n')
            print('<index-output-path>: \nthe path to store the index ->> example: /home/user/ColBERT')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputpath = arg

    return inputfile, outputpath

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

    # replace the inputfile name with outputfile name
    outputtsv = inputfile.replace(".json", ".tsv")

    with open(outputtsv, 'w', encoding="utf-8") as f:
        tsv_w = csv.writer(f, delimiter='\t', lineterminator='\n')
        # tsv_w.writerow(['label', 'question'])
        for num in range(len(lines)):
            tsv_w.writerow([label[num], question[num]])
    
    return outputtsv

def indexer(checkpointp, index_name, collection, outputpath):
    experiment = 'liveindex'
    index_folder = 'experiments/' + experiment + '/indexes/'
    nbits = 2   # encode each dimension with 2 bits
    doc_maxlen = 300   # truncate passages at 300 tokens
    collection = os.path.join(collection)
    collection = Collection(path=collection)
    checkpoint = checkpointp
    index_name = f'{index_name}.{nbits}bits'


    with Run().context(RunConfig(nranks=1, experiment= experiment)):  # nranks specifies the number of GPUs to use.
        config = ColBERTConfig(doc_maxlen=doc_maxlen, nbits=nbits)

        indexer = Indexer(checkpoint=checkpoint, config=config)
        indexer.index(name=index_name, collection=collection, overwrite=True)
    
    # delete exist index
    if os.path.exists(outputpath + "/" + index_name):
        os.system("rm -rf " + outputpath + "/" + index_name)
    # move the index to the output path
    os.system("mv " + index_folder + index_name + " " + outputpath)
    # print index path
    print("Index path: " + outputpath + "/" + index_name)
    # remove experiment folder
    os.system("rm -rf experiments/")

if __name__ == "__main__":
    inputfile, outputpath = getvalue(sys.argv[1:])
    collection = jsontotsv(inputfile)
    indexer(checkpointp, index_name, collection, outputpath)
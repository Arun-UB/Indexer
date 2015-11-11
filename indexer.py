#! /usr/bin/python
import argparse
import re
import collections
from math import log
import operator
import json

class Posting:
    '''Class for storing the documnet ID and the term frequecny'''
    def __init__(self, docId, tf):
        self.docId = docId
        self.tf = tf

def add_to_index(term,docId,index):
    if term in index:
        if index[term][-1].docId == docId:
            index[term][-1].tf+=1
        else:
            index[term].append(Posting(docId,1))
    else:
        index[term] = [Posting(docId,1)]

def add_line(terms,docId,index,term_count):
    for term in terms:
        isNum = re.search(r'\d+',term)
        if not isNum:
            term_count[docId] += 1
            add_to_index(term,docId,index)

def write_index(index,filename):
    '''Write the index to a file '''
    with open(filename,"w+") as f:
        for term in index:
            l = ""
            for d in index[term]:
                l+=str(d.docId) + "," + str(d.tf) + ";"
            f.write(term + "|" + l + "\n")


def get_corpus(corpus_file,index_file):
    '''Reads the corpus file and prepares the index'''
    index = {}
    term_count = {}
    bm25 = {}    
    with open(corpus_file) as f:
        for page in f:
            m = re.search(r'^# \d+\s',page)
            if m:
                docId = m.group().strip()
                term_count[docId] = 0
            add_line(page.split(),docId,index,term_count)

    with open("term_count.json","w") as f:
            f.write(json.dumps(term_count))
    write_index(index,index_file)
        
if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Index a file")
    parser.add_argument('src', metavar="Corpus", help="Corpus filename")
    parser.add_argument('dst', metavar="Index", help="Index filename")
    args = parser.parse_args()
    get_corpus(args.src, args.dst)



            

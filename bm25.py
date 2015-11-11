#! /usr/bin/python
import argparse
import re
import collections
from math import log
import operator
import json

def compute_bm25(p,N,n,qf,avdl,term_count,bm25):
    '''Compute the bm25 for the given term'''
    p = p.split(',')
    docId = p[0]
    tf = float (p[1])
    k1 = 1.2
    k2 = 100
    b  = 0.75
    t1 = (N - n + 0.5)/(n+0.5)
    K =  k1 * (((1-b)) + b * ((float(term_count[docId]))/avdl))
    t2 = (k1 + 1) * tf/(K + 1.2)
    t3 = (k2 +1) * float(qf) / (k2 + qf)
    if docId in bm25:
        bm25[docId] += log(t1*t2*t3)
    else:
        bm25[docId] = log(t1*t2*t3)

def get_bm25(index_file,term,N,qf,avdl,term_count,bm25):
    '''Computes bm25 for each term in the query'''
    with open(index_file) as input_data:
        for line in input_data:
            m =re.search('^'+term + '\|' ,line)
            if m:
                term = '^' + term + '\|'
                line = re.sub(term,'',line)
                n = line.count(';')
                for doc in (line.split(";"))[:-1]:
                    compute_bm25(doc,N,n,qf,avdl,term_count,bm25)    

def write_bm25(bm25,filename,max_num,q):
    '''Writes the bm25 ranks to a file in the suggested format'''
    bm25_l = sorted(bm25.items(), key=operator.itemgetter(1),reverse=True)
    bm25_l = bm25_l[:int(max_num)]
    rank = 0
    with open(filename,"a+") as f:
        for t in bm25_l:
            rank+=1
            l=str(q) + " Q0 " + str(t[0]) + " " + str(rank) + " " + str(t[1]) + " bm25_ab_01"
            print(l)
            f.write(l + "\n")

def get_query(index_file,query,N,avdl,term_count,bm25):
    '''Read the query file'''
    ql = query.split()
    ql = collections.Counter(ql)
    for term in ql:
        get_bm25(index_file,term,N,ql[term],avdl,term_count,bm25)


def get_avdl(term_count,N):
    '''Calculate the average document length'''
    tc = 0
    for t in term_count:
        tc+=term_count[t]
    return (tc/N)

def get_queries(index_file,queries_file,max_num):
    '''Read the query file and prepare the results file'''
    q = 0
    '''Read the term count file produced by the indexer'''
    with open('term_count.json') as json_data:
        term_count = json.load(json_data)

    N = len(term_count)
    avdl = get_avdl(term_count,N)
    open("results.eval", 'w').close()
    '''Read the query file'''
    with open(queries_file) as input_data:
        for line in input_data:
            q+=1
            bm25 = {}
            get_query(index_file,line,N,avdl,term_count,bm25)
            write_bm25(bm25,"results.eval",max_num,q)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Index a file")
    parser.add_argument('ind', metavar="INDEX_FILE", help="Index filename")
    parser.add_argument('q', metavar="QUERIES_FILE", help="Queries filename")
    parser.add_argument('max_num', metavar="MAX_RESULTS", help="Maximum number of document")
    args = parser.parse_args()
    get_queries(args.ind, args.q, args.max_num)
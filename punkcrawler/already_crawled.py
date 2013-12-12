#!/usr/bin/python

import sys
import pickle
from pnk_logging import pnk_log
import traceback

already_crawled_filename = ".__tmp__.already-crawled"

def init():
    f = open(already_crawled_filename, "w")
    pickle.dump([], f)
    f.close()
    
def add_to_already_crawled():

    mod = __file__
    urls_to_add = []
    for line in sys.stdin:

        try:
            domain, urlin_clean = line.split("\t")
            domain = domain.strip()
            urlin_clean = urlin_clean.strip()
            urls_to_add.append(normalize_url(urlin_clean))
    
        except:
            pnk_log(mod, "Bad line in file: %s" % line)
            continue
    
    f = open(already_crawled_filename, "rb")

    already_crawled_list = pickle.load(f)
    already_crawled_list = already_crawled_list + urls_to_add
    f.close()

    f = open(already_crawled_filename, "wb")
    pickle.dump(list(set(already_crawled_list)), f)
    f.close()

def normalize_url(url):
        
    if url[-1] == "/":
        url = url[:-1]

    return url

if __name__ == "__main__":
    
    try:
        if sys.argv[1] == "--init":
            init()
        elif sys.argv[1] == "--add-db-to-crawled":
            add_to_already_crawled()
    except:
        print "Usage: --init or --add-db-to-crawled"
        traceback.print_exc()
    

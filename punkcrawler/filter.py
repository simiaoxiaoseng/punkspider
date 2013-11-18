import sys
from urlparse import urlparse
import pickle
import os

filter_pickle_filename = ".__tmp__.filter-domains"
    
def load(seed_filename):
    f = open(seed_filename, "r")
    hosts_constrained = []

    for url in f:
        host = urlparse(url.strip()).netloc.split(":")[0]
        if host not in hosts_constrained:
            hosts_constrained.append(host)
            
    pickle.dump(hosts_constrained, open(filter_pickle_filename, 'w'))
    
def filter_by_domain(infilename, domain_list):

    for url in open(infilename, 'r'):
        url_clean = url.strip()
        if urlparse(url_clean).netloc.split(":")[0] in domain_list:
            print url_clean
            
if __name__ == "__main__":

    #python filter.py urls.txt --load-filter
    if sys.argv[2] == "--load":
        load(sys.argv[1])
    
    #python filter.py urls.txt --filter
    if sys.argv[2] == "--filter":
        domains_to_filter_by = pickle.load(open(filter_pickle_filename))
        filter_by_domain(sys.argv[1], domains_to_filter_by)    
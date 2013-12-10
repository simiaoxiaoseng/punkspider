import sys
from urlparse import urlparse
import pickle
import traceback

filter_pickle_filename = ".__tmp__.filter-domains"
already_crawled_pickle_filename = ".__tmp__.already-crawled"
        
def load(seed_filename):

    f = open(seed_filename, "r")
    hosts_constrained = []

    for line in f:
        host = line.split("\t")[0].strip()
        if host not in hosts_constrained:
            hosts_constrained.append(host)
            
    pickle.dump(hosts_constrained, open(filter_pickle_filename, 'w'))
    
def filter_by_domain(infilename, domain_list):

    for line in open(infilename, 'r'):

        try:
            domain, url = line.split("\t")
            url_clean = url.strip()
            domain = domain.strip()
            if domain in domain_list:
                print domain + "\t" + url_clean
                
        except:
            traceback.print_exc()

def filter_only_root_urls(infilename):

    for line in open(infilename, 'r'):

        try:
            domain, url = line.split("\t")
            url_clean = url.strip()
            url_parsed = urlparse(url_clean)
            domain = domain.strip()
    
            if not url_parsed.path and not url_parsed.params\
            and not url_parsed.query and not url_parsed.fragment:
                print domain + "\t" + url_clean
        except:
            traceback.print_exc()
                        
if __name__ == "__main__":

#    try:
    #python filter.py urls.txt --load-filter
    if sys.argv[2] == "--load":
        load(sys.argv[1])
    
    #python filter.py urls.txt --filter
    if sys.argv[2] == "--filter":
        domains_to_filter_by = pickle.load(open(filter_pickle_filename))
        filter_by_domain(sys.argv[1], domains_to_filter_by)    
        
    #python filter.py urls.txt --filter
    if sys.argv[2] == "--filter-only-root":
        filter_only_root_urls(sys.argv[1])
            
#    except:
#        print "Usage: python filter.py <file> (--load-filter | --filter | --filter-only-root)"
    

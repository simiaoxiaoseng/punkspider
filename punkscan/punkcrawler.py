####################################################################
#  Hyperion Gray, LLC - PunkCRAWLER                                #
####################################################################
#                                                                  #
#  This script is an automatic configur-er and wrapper for         #
#  PunkCRAWLER crawls. It first limits the domains we want to crawl#
#  by pulling from your Solr Summary instance. It reads from       #
#  punkscan_configs/punkscan_config.cfg and then performs a crawl, #
#  reduces the results down to specific cases, and dumps the       #
#  results to a directory. This is is generally followed by        #
#  running punkSCAN - which fuzzes the relevant found URLs         #
#                                                                  #
####################################################################  

import os
import sys
import codecs
import subprocess
from urlparse import urlparse
from urlparse import parse_qs
cwdir = os.path.dirname(__file__)
punkscan_base = os.path.join(cwdir, ".")
sys.path.append(os.path.join(punkscan_base, "hadooper"))
sys.path.append(os.path.join(punkscan_base, "config_scripts"))
sys.path.append(os.path.join(punkscan_base, "crawl_db_parser"))
sys.path.append(os.path.join(punkscan_base, "crawler"))
sys.path.append(os.path.join(punkscan_base, "punk_solr"))
import punkscan_solr
from ConfigParser import SafeConfigParser

config_parser = SafeConfigParser()
config_parser.read(os.path.join(punkscan_base,'punkscan_configs', 'punkscan_config.cfg'))


def configure_punkscan():
    '''Configure punkscan, get ready for the crawl.
    Mark vscan_tstamp in Solr.'''

    punk_solro = punkscan_solr.PunkSolr()
    #get the urls to scan
    solr_urls_dic = punk_solro.get_scanned_longest_ago()

    #mark urls as scan attempted with vscan_tstamp
    punk_solro.update_vscan_tstamp_batch(solr_urls_dic)
    
    f = open("../punkcrawler/urls/urls", "w")
    for url_dic in solr_urls_dic:
        try:
            f.write(url_dic["url"])
            f.write("\n")
        except:
            #silently fail, should probably log failed attempt, but that would likely fail...
            pass
                
def crawl():
    '''Perform the crawl against the sites'''

    subprocess.Popen("../punkcrawler/punkcrawler -dc", shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()[0]    

def parse_crawl_db():
    '''Delete previous crawl db on HDFS and local fs,
    Dump the crawl db to HDFS, copy from HDFS to local
    filesystem'''

    f = open("../punkcrawler/db/urls.db", "r")
    for line in f:
        url = line.split("\t")[1]
        yield url

def crawl_db_reduce(crawl_db_generator):
    '''Goes through the crawldb and removes duplicate
    URLs with the same query keys but different values.
    Note this also applies to URLs without queries, we just
    keep one of those. We will at least end up with one URL
    to run in the mapreduce punk_fuzz job, which is a requirement.
    This step significantly reduces the amount of data processed
    by the mapreduce job.'''
    
    #append url query_domain keys to list_of_keys and the url to url_list if we have not seen it
    #in a prevoius iteration. Else just move along. url_list will then be a list of
    #urls with unique keys
    list_of_keys = []
    url_list = []

    for url in crawl_db_generator:

        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        #get a list of the query keys
        query_keys = parse_qs(parsed_url.query).keys()

        #if there are no query keys and we have not done so already
        #add the domain to the list. This ensures there is at least
        #one URL for the domain sent to the mapreduce job. This is a
        #requirement.
        
        if not query_keys and domain not in list_of_keys:

            url_list.append(url)
            list_of_keys.append(domain)


        #set up a unique string for unique query keys on a
        #domain. A concat of the query key + "_" + domain.

        url_keys = [x+ '_' + domain for x in query_keys]

        #Assuming there's a query string, if the url key
        #is not in the list of keys we have already seen
        #append the url, otherwise skip it
        
        if query_keys and url_keys not in list_of_keys:

            list_of_keys.append(url_keys)
            url_list.append(url)

    return url_list
            
def execute():

    #configure and run punkscan, then filter and prepare URLs to be fuzzed
    configure_punkscan()
    crawl()
    f = open(os.path.join(punkscan_base, "punk_fuzzer", "urls_to_fuzz"), 'w')

    for url in crawl_db_reduce(parse_crawl_db()):

        f.write(url)
        f.write("\n")
                    
if __name__ == "__main__":

    execute()
                

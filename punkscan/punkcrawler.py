####################################################################
#  Hyperion Gray, LLC - PunkCRAWLER                                #
####################################################################
#                                                                  #
#  This script is an automatic configur-er and wrapper for Apache  #
#  Nutch crawls. It first limits the domains we want to crawl by   #
#  pulling from your Solr Summary instance. It reads from          #
#  punkscan_configs/punkscan_config.cfg and then performs a crawl, #
#  reduces the results down to specific cases, and dumps the       #
#  results to a directory. This is is generally followed by        #
#  running punkSCAN - which fuzzes the relevant found URLs         #
#                                                                  #
####################################################################  
'''
-------begin example config---------------------

[directories]

# These need to be set to your HADOOP_HOME and NUTCH_HOME directories
HADOOP_HOME = /usr/local/hadoop
NUTCH_HOME = /usr/local/punkscan/nutch

[performance]

# These values should be tweaked based on your specific scenario, generally the
# number of sites you are hoping to crawl and fuzz in one round of jobs are the
# dependencies for these values.

sim_urls_to_scan = 120  # <----- Defines how many urls to scan simultaneously
depth = 2  # <---- Defines the number of generate-fetch-parse-db update cycles for Apache Nutch
topN = 5000 # <---- The number of URLs to keep per Nutch cycle

[urls]

# Your Solr detail and Solr Summary URLs - see PunkSCAN tutorial for additional info

solr_details_url = http://localhost:8080/solr/detail/
solr_summary_url = http://localhost:8080/solr/summary/

[users]

#The user that Hadoop is run as
hadoop_user = pgotsr

[hadoop]

# csv list of hadoop datanodes - NOT including the machine that punkscan
# is being run from

datanodes = slave1,slave2,slave3,slave4

---------end example config---------------------


Usage: python punkcrawler.py

'''

import os
import sys
from urlparse import urlparse
from urlparse import parse_qs
cwdir = os.path.dirname(__file__)
punkscan_base = os.path.join(cwdir, ".")
sys.path.append(os.path.join(punkscan_base, "hadooper"))
sys.path.append(os.path.join(punkscan_base, "config_scripts"))
sys.path.append(os.path.join(punkscan_base, "crawl_db_parser"))
sys.path.append(os.path.join(punkscan_base, "crawler"))
import reconfig_nutch
import crawldb_parser
import hadooper
import nutch
from ConfigParser import SafeConfigParser
config_parser = SafeConfigParser()
config_parser.read(os.path.join(punkscan_base,'punkscan_configs', 'punkscan_config.cfg'))
HADOOP_HOME=config_parser.get('directories','HADOOP_HOME')
NUTCH_HOME=config_parser.get('directories','NUTCH_HOME')

def configure_punkscan():
    '''Configure punkscan, get ready for the crawl.
    Mark vscan_tstamp in Solr.'''

    config_r = reconfig_nutch.ConfigoRoboto()
    config_r.generate_template_file()
    config_r.generate_seed_list()
    config_r.clear_and_put_seed_list_on_hdfs()

def crawl():
    '''Perform the crawl against the sites'''

    nutch.NutchController().crawl()

def parse_crawl_db():
    '''Delete previous crawl db on HDFS and local fs,
    Dump the crawl db to HDFS, copy from HDFS to local
    filesystem'''

    db_parso = crawldb_parser.CrawlDBParser()
    db_parso.dump_crawl_db()
    db_parso.get_crawl_db_dump()
    return db_parso.crawl_db_url_generator()

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

    configure_punkscan()
    crawl()
    f = open(os.path.join(punkscan_base, "punk_fuzzer", "urls_to_fuzz"), 'w')

    for url in crawl_db_reduce(parse_crawl_db()):

        f.write(url)
        f.write("\n")
                    
if __name__ == "__main__":

    execute()
                

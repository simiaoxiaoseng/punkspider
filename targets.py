#!/usr/bin/env python

# Created by Hyperion Gray, LLC
# Released under the Apache 2.0 License

#usage: python targets.py [targets csv file]

import sys
import os
import datetime
from urlparse import urlparse
cwdir = os.path.dirname(__file__)
punkscan_base = os.path.join("punkscan/")
sys.path.append(os.path.join(punkscan_base, "punk_solr", "pysolr"))
import pysolr
from ConfigParser import SafeConfigParser
config_parser = SafeConfigParser()
config_parser.read(os.path.join(punkscan_base,'punkscan_configs', 'punkscan_config.cfg'))

class Targets:
    '''Deal with targets'''

    def __init__(self):

        self.conn = pysolr.Solr(config_parser.get('urls', 'solr_summary_url'))

    def __val_std_url(self, url):
        '''Validate a url and standardize it'''    

        if url[-1] == "/":
            url = url[:-1]

        parsed_url = urlparse(url)

        if parsed_url[2]:
            raise Exception("Targets should not contain paths" % url)

        return url + "/"

    def read_from_csv(self, tfile):
        '''Add targets from csv file'''

        f = open(tfile, 'r')
        solr_docs = []

        for line in f:

            spl = line.split(";")
            url = self.__val_std_url(spl[0])
            title = spl[1]
            dt = datetime.datetime.now()
            solr_doc = {"id": url, "url": url, "title": title, "tstamp": dt}
            solr_docs.append(solr_doc)

        self.conn.add(solr_docs)

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print "Usage: python targets.py [targets csv file]"
        sys.exit(0)
    
    if sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print "Usage: python targets.py [targets csv file]"
        sys.exit(0)
    
    Targets().read_from_csv(sys.argv[1])
    
    

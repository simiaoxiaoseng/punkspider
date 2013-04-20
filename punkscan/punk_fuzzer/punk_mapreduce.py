#!/usr/bin/env python

# Created by Hyperion Gray, LLC
# Released under the Apache 2.0 License

import os
import sys
from mrjob.job import MRJob
from urlparse import urlparse
from urlparse import parse_qs
import requests
cwdir = os.path.dirname(__file__)
sys.path.append(os.path.join(cwdir,"mapreduce_indexer"))
sys.path.append(os.path.join(cwdir,"punk_fuzz"))
sys.path.append(cwdir)
import punk_fuzz
import mapreduce_indexer

class PunkFuzzDistributed(MRJob):

    def mapper(self, key, url):
        '''Yield domain as the key, and parameter to be fuzzed as the value'''

        #takes in <None, url> as the <key, value> of the mapper input

        mapper_punk_fuzz = punk_fuzz.PunkFuzz()
        parsed_url = urlparse(url)
        domain = parsed_url.scheme + "://" + parsed_url.netloc + "/"

        if mapper_punk_fuzz.check_if_param(parsed_url):

            parsed_url_query = parsed_url.query
            url_q_dic = parse_qs(parsed_url_query)

            for query_param, query_val in url_q_dic.iteritems():

                #and now we fuzz
                mapper_punk_fuzz.punk_set_target(url, query_param)
                vuln_list = mapper_punk_fuzz.fuzz()

                #output vuln_list and domain for each url and query param pair
                yield domain, vuln_list

    def reducer(self, domain, vuln_lists):

        full_vuln_list = []

        #iterate over all lists of vulnerabilities corresponding to a single domain
        for vuln_list in vuln_lists:
        
            full_vuln_list = full_vuln_list + vuln_list

        #win
        mapreduce_indexer.PunkMapReduceIndexer(domain, full_vuln_list, reducer_instance = self).add_vuln_info()

        yield domain, full_vuln_list

if __name__ == '__main__':

    PunkFuzzDistributed.run()

import os
import sys
from mrjob.job import MRJob
from urlparse import urlparse
from urlparse import parse_qs
import requests
cwdir = os.path.dirname(__file__)
sys.path.append(os.path.join(cwdir,"mapreduce_indexer"))
sys.path.append(os.path.join(cwdir,"punk_fuzz"))
import punk_fuzz
import mapreduce_indexer


class PunkFuzzDistributed(MRJob):

    def mapper_init(self):

        self.mapper_punk_fuzz = punk_fuzz.PunkFuzz()

    def reducer_init(self):

        self.reducer_punk_fuzz = punk_fuzz.PunkFuzz()

    def mapper(self, key, url):
        '''Yield domain as the key, and parameter to be fuzzed as the value'''

        parsed_url = urlparse(url)
        domain = parsed_url.scheme + "://" + parsed_url.netloc + "/"

        if self.mapper_punk_fuzz.check_if_param(parsed_url):

            parsed_url_query = parsed_url.query
            url_q_dic = parse_qs(parsed_url_query)

            for query_param, query_val in url_q_dic.iteritems():

                #yielding a tuple in mrjob will yield a list, but for
                #consistency we yield a tuple and mrjob will handle it
                
                yield domain, (url, query_param)

    def reducer(self, domain, url_query_params):
        '''The key in this reduce job is the domain. It yields a list of vulnerabilities
        as the values. It will combine '''

        #reducer should take the urls as the key and output a dictionary of vulnerabilities per each URL,
        #reducing the <url, query param> to <url, all_vuln_list> all_vuln_list is a list of vulns of the form
        #[[vuln_url, payload, vuln_type], etc.]

        vuln_list = []
        for url_query_param in url_query_params:

            url_to_fuzz = url_query_param[0]
            param_to_fuzz = url_query_param[1]

            self.reducer_punk_fuzz.set_target(url_to_fuzz, param_to_fuzz)
            fuzzer_vuln_list = self.reducer_punk_fuzz.fuzz()

            for vuln in fuzzer_vuln_list:

                vuln_list.append(vuln)

        #index this stuff to Solr
        mapreduce_indexer.PunkMapReduceIndexer(domain, vuln_list).add_vuln_info()

        yield domain, vuln_list

if __name__ == '__main__':

    PunkFuzzDistributed.run()

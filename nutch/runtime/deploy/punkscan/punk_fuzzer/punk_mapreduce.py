from mrjob.job import MRJob
from urlparse import urlparse
from urlparse import parse_qs
import requests
import punk_fuzz

class PunkFuzzDistributed(MRJob):

    def mapper_init(self):

        self.mapper_punk_fuzz = punk_fuzz.PunkFuzz()

    def reducer_init(self):

        self.reducer_punk_fuzz = punk_fuzz.PunkFuzz()

    def mapper(self, key, url):
        '''Yield all URL as the key, and parameter to be fuzzed as the value'''

        parsed_url = urlparse(url)

        if self.mapper_punk_fuzz.check_if_param(parsed_url):

            parsed_url_query = parsed_url.query
            url_q_dic = parse_qs(parsed_url_query)

            for query_param, query_val in url_q_dic.iteritems():
        
                yield url, query_param

    def reducer(self, url, param_to_replace):
        '''The key in this mapreduce job is the url, param_to_replace is a generator that yields
        all values yielded by the mapper'''

        for param in param_to_replace:

            
            #make requests and fuzz each url
            #this will automatically distribute fuzzing through hadoop

            yield url, param

if __name__ == '__main__':
    PunkFuzzDistributed.run()

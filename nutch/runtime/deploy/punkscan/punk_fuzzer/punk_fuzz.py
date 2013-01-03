#!/usr/bin/env python
from urlparse import urlparse
from urlparse import urlunparse
from urlparse import parse_qs
from urllib import urlencode
from urllib import quote_plus
import os
import sys
cwdir = os.path.dirname(__file__)
sys.path.append(os.path.join(cwdir,  "fuzzer_config"))
sys.path.append(os.path.join(cwdir,  "beautifulsoup"))
sys.path.append(cwdir)

#add when running in mr job
import fuzz_config_parser
import requests
from bs4 import BeautifulSoup

#will this work in mrjob?
cwdir = os.path.dirname(__file__)
punkscan_base = os.path.join(cwdir, "../")
from ConfigParser import SafeConfigParser
config_parser = SafeConfigParser()
config_parser.read(os.path.join(punkscan_base,'punkscan_configs', 'punkscan_config.cfg'))

class GenFuzz:
    '''Series of methods useful in the individual fuzzing objects'''

    def __init__(self):

        self.fuzz_config = fuzz_config_parser.ConfigO()

        #get various payloads
        self.xss_payloads = self.fuzz_config.get_xss_strings()
#       self.sqli_payloads =
#       self.bsqli_payloads = 

    def mutate_append(self, payload_list, str_to_append):
        '''Takes in a list of strings to append to append to the payloads,
        appends to and returns list taken in'''

        mutated_list = []
        for payload in payload_list:

            appended_payload = payload + str_to_append
            mutated_list.append(appended_payload)

        full_list = mutated_list + payload_list

        return full_list
        
    def mutate_prepend(self, payload_list, str_to_prepend):
        '''Takes in a list of strings to prepend to prepend to the payloads,
        prepends to and returns list taken in'''

        mutated_list = []
        for payload in payload_list:

            prepended_payload = str_to_prepend + payload
            mutated_list.append(prepended_payload)

        full_list = mutated_list + payload_list

        return full_list

    def mutate_replace(self, payload_list, str_to_replace, str_to_replace_with):
        '''Takes in a list of strings, appends to the list those same strings
        with str_to_replace_with in place of str_to_replace if the string was changed'''

        mutated_list = []
        for payload in payload_list:

            payload_replaced = payload.replace(str_to_replace, str_to_replace_with)
            if payload_replaced != payload_list:

                mutated_list.append(payload_replaced)


        full_list = mutated_list + payload_list

        return full_list

    def mutate_urlencode(self, list_to_enc):
        '''Takes in a list of strings to add encoded payloads to,
        appends to and returns list taken in. Note the way that
        we are doing requests, this will end up double-url encoding
        before the web server receives the info'''

        list_to_enc_copy = list(list_to_enc)
        list_enc = [quote_plus(x) for x in list_to_enc_copy]

        full_list = list_to_enc_copy + list_enc        

        return full_list
        
    def check_if_param(self, url):
        '''Check if a URL has parameters, if it does return true, if not return false'''

        if not url.query:
            
            return False

        else:
            return True

    def set_target(self, url, param):
        '''Set the target url-parameter pair'''

        self.url = url
        self.param = param
        self.proxy = self.fuzz_config.get_proxies_dic()
        
        try:
            self.url_parsed = urlparse(self.url)
            self.protocol = self.url_parsed.scheme
            return self.url_parsed

        except:
            raise Exception("Cannot parse url %s" % self.url)

    def replace_param(self, replacement_string):
        '''Replace a parameter in a url with another string.
        Will be used extensively in fuzzing'''
        
        query_dic = parse_qs(self.url_parsed.query)
        query_dic[self.param] = replacement_string

        #this incidentally will also automatically url-encode the payload (thanks urlencode!)
        query_reassembled = urlencode(query_dic, doseq = True)

        #3rd element is always the query, replace query with our own

        url_list_parsed = list(self.url_parsed)
        url_list_parsed[4] = query_reassembled
        url_parsed_q_replaced = tuple(url_list_parsed)

        url_reassembled = urlunparse(url_parsed_q_replaced)
        
        return url_reassembled

    def generate_urls_gen(self, final_payload_list):

        for payload in final_payload_list:
            
            fuzzy_url = self.replace_param(payload)
            yield (fuzzy_url, payload)

    def url_response_gen(self, url_gen):
        '''Takes in a (full fuzzed request URL, payload) generator and returns a (url,
        payload, response) generator.'''

        for url_payload in url_gen():

            url = url_payload[0]
            payload = url_payload[1]

            r = requests.get(url, proxies = self.proxy)

            yield (url, payload, r.text)

    def search_urls_tag(self, url_response_gen, match_string, vuln_type, tag = False, attribute = False):
        '''Takes in a (url, payload, response) generator and returns a list
        of (url, payload, vuln_type) that appear to be vulnerable through a string match
        in a tag'''

        if not tag and not attribute:
            
            raise Exception("Neither tag nor attribute are set")

        vulnerable_url_list = []
        for url_response in url_response_gen:

            url_payload_info = (url_response[0], url_response[1], vuln_type, self.param, self.protocol)
            soup = BeautifulSoup(url_response[2])

            for tag_in_page in soup.find_all(tag):

                #if tag is set, look in the tag's string
                if tag:
                    tag_string = tag_in_page.string

                    if tag_string and match_string in tag_string:
                        vulnerable_url_list.append(url_payload_info)

                #if attribute is set, look in the attribute's string
                if attribute:
                    attribute_string = tag_in_page.get(attribute)

                    if attribute_string and match_string in attribute_string:
                        vulnerable_url_list.append(url_payload_info)

                #stop once we find a vulnerability in tag, attribute, or both
                #in one iteration
                
                if vulnerable_url_list:
                    return vulnerable_url_list

        return vulnerable_url_list

class XSSFuzz(GenFuzz):
    '''This class fuzzes a single URL-parameter pair with a simple xss fuzzer'''

    def __init__(self):

        GenFuzz.__init__(self)

    def xss_set_target(self, url, param):
        '''Set the target'''
        
        self.target = self.set_target(url, param)

    def __xss_make_payloads(self):
        '''Set various mutations for xss payloads'''

        #mutate payloads
        xss_string_list_add_mut_prep = self.mutate_prepend(self.xss_payloads, '">')
        xss_string_list_add_enc = self.mutate_urlencode(xss_string_list_add_mut_prep)
        final_list = self.mutate_replace(xss_string_list_add_enc, '"', "'")

        #return list of all payloads
        return final_list
        
    def __xss_url_gen(self):
        '''Yield URLs that are to be XSS requests'''

        return self.generate_urls_gen(self.__xss_make_payloads())

    def __xss_get_url_responses(self):
        '''Yield responses - takes in a url generator and outputs
        a response generator'''

        return self.url_response_gen(self.__xss_url_gen)

    def xss_fuzz(self):
        '''Returns a list of (vulnerable url, payload) tuples'''

        return self.search_urls_tag(self.__xss_get_url_responses(),  "alert(313371234)", "xss", tag="script")

class SQLiFuzz(GenFuzz):

    def __init__(self):

        GenFuzz.__init__(self)

    def sqli_set_target(self, url, param):
        '''Set the target '''

        self.target = self.set_target(url, param)

    def __sqli_make_payloads(self):

        pass
        #mutate payloads


        #return final list of payloads

class PunkFuzz(GenFuzz):
    '''A utility class that uses all of the fuzzing objects'''

    def __init__(self):
        '''Initialize fuzzing modules'''

        self.xss_fuzzer = XSSFuzz()

    def set_target(self, url, param):
        '''Set the targets for the fuzzers '''

        self.xss_fuzzer.xss_set_target(url, param)

    def fuzz(self):
        '''Perform the fuzzes and collect (vulnerable url, payload) tuples '''

        self.xss_fuzz_results = self.xss_fuzzer.xss_fuzz()

        return self.xss_fuzz_results

if __name__ == "__main__":

    x = PunkFuzz()
    x.set_target("http://www.mysticboarding.com/dealers/distributors/?did=123", "did")
    print x.fuzz()
#    x = XSSFuzz()
#    x.xss_set_target("http://www.mysticboarding.com/dealers/distributors/?did=", "did")
#    print x.xss_fuzz()



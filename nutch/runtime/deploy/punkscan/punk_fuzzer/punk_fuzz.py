from urlparse import urlparse
from urlparse import urlunparse
from urlparse import parse_qs
from urllib import urlencode

class PunkFuzz:

    def __init__(self):

        pass

    def check_if_param(self, url):
        '''Check if a URL has parameters, if it does return true,if not return false'''

        if not url.query:
            return False

        else:
            return True

    def url_encode(self, string_to_encode):

        pass

    def double_url_encode(self, string_to_encode):

        pass

    def mutate(self, string_to_mutate, mutation_rule):

        pass

    def replace_param(self, url, param, replacement_string):

        try:
            url_parsed = urlparse(url)

        except:
            
            #must add something here in case of failure
            pass

        query_dic = parse_qs(url_parsed.query)
        query_dic[param] = replacement_string
        query_reassembled = urlencode(query_dic, doseq=True)

        #3rd element is always the query, replace query with our own
        url_list_parsed = list(url_parsed)
        url_list_parsed[4] = query_reassembled
        url_parsed_q_replaced = tuple(url_list_parsed)

        url_reassembled = urlunparse(url_parsed_q_replaced)
        
        return url_reassembled

if __name__ == "__main__":

    print PunkFuzz().replace_param("www.google.com/?q=blah&q2=blah2&q=whatever","q","ddd")

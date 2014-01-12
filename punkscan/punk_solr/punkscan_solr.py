# Created by Hyperion Gray, LLC
# Released under the Apache 2.0 License

import sys
import json
import os
cwdir = os.path.dirname(__file__)
punkscan_base = os.path.join(cwdir, "../")
sys.path.append(os.path.join(punkscan_base,"punk_fuzzer/", "fuzzer_config/"))
sys.path.append(os.path.join(punkscan_base,"punk_fuzzer/"))
import fuzz_config_parser
from datetime import datetime
import requests
import traceback
from urlparse import urljoin
import urllib
from ConfigParser import SafeConfigParser
config_parser = SafeConfigParser()
config_parser.read(os.path.join(punkscan_base,'../', 'punkcrawler', 'punkcrawler.cfg'))

class PunkSolr:

    def __init__(self):

        configo = fuzz_config_parser.ConfigO()
        solr_urls_dic = configo.get_solr_urls()
        self.index_proxies = configo.get_index_proxies_dic()

        self.solr_summary_url = solr_urls_dic['solr_summary_url']
        self.solr_details_url = solr_urls_dic['solr_details_url']

        #may need to reduce # of commits
        self.solr_summary_url_update = urljoin(self.solr_summary_url, "summary/update/json/?commit=true")
        
        self.solr_summary_url_query = urljoin(self.solr_summary_url, "summary/select")
        self.solr_details_url_update = urljoin(self.solr_details_url, "detail/update/json/?commit=true")
        
        self.num_urls_to_scan = configo.get_item('fuzz_configs/sim_urls_to_scan')

    def query_summ(self, query, rows = 10, sort = None):
        
        query_dic = {"q": query, "wt" : "json", "rows" : rows}
        
        if sort:
            query_dic["sort"] = sort
        
        query = urllib.urlencode(query_dic)
        full_query_url = self.solr_summary_url_query + "/?%s" % query
        get_request = requests.get(full_query_url, proxies = self.index_proxies)
        raw_results = get_request.text
        return_code = get_request.status_code

        if return_code != 200:
            raise Exception("Query didn't return 200 OK")
        
        return json.loads(raw_results)["response"]["docs"]
        
    def add_summ(self, docs_list):
        '''docs_list is a dictionary of documents (not a JSON string)'''

        post_request = requests.post(self.solr_summary_url_update, proxies = self.index_proxies, data = json.dumps(docs_list))
        
        return_code = post_request.status_code
        return_text = post_request.text

        if return_code != 200:
            raise Exception("Add didn't return 200 OK, returned %s with return text %s" % (str(return_code), return_text))

    def delete_detail(self, query):
        
        delete_data = {"delete" : {"query" : query}}
        post_request = requests.post(self.solr_details_url_update, proxies = self.index_proxies, data = json.dumps(delete_data))

        return_code = post_request.status_code
        return_text = post_request.text

        if return_code != 200:
            raise Exception("Delete didn't return 200 OK, returned %s with return text %s" % (str(return_code), return_text))

    def add_detail(self, docs_list):
        '''docs_list is a dictionary of documents (not a JSON string)'''

        post_request = requests.post(self.solr_details_url_update, proxies = self.index_proxies, data = json.dumps(docs_list))
        
        return_code = post_request.status_code
        return_text = post_request.text

        if return_code != 200:
            raise Exception("Add_detail didn't return 200 OK, returned %s with return text %s" % (str(return_code), return_text))
        
    def get_scanned_longest_ago(self):
        '''This gets the record from solr that was scanned longest ago, it starts with those that have no vscan timestamp'''
        
        scanned_longest_ago_or_not_scanned_dic = self.query_summ('*:*', sort='vscan_tstamp asc', rows=self.num_urls_to_scan)

        return scanned_longest_ago_or_not_scanned_dic

    def update_vscan_tstamp_batch(self, solr_results):
        
        for result in solr_results:
            result["vscan_tstamp"] = str(datetime.now().isoformat() + "Z")
            
        self.add_summ(solr_results)

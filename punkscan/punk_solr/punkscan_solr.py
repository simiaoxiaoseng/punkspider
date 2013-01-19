# Created by Hyperion Gray, LLC
# Released under the Apache 2.0 License

import sys
import os
import datetime
cwdir = os.path.dirname(__file__)
punkscan_base = os.path.join(cwdir, "../")
sys.path.append(os.path.join(cwdir,"pysolr/"))
import pysolr
from ConfigParser import SafeConfigParser
config_parser = SafeConfigParser()
config_parser.read(os.path.join(punkscan_base,'punkscan_configs', 'punkscan_config.cfg'))

class PunkSolr:

    def __init__(self):

        self.conn = pysolr.Solr(config_parser.get('urls', 'solr_summary_url'))
        self.num_urls_to_scan = config_parser.get('performance', 'sim_urls_to_scan')

    def get_record_by_id(self):

        solr_doc_pull = self.conn.search('id:' + '"' + url + '/"')

        return solr_doc_pull

    def get_scanned_longest_ago(self):
        '''This gets the record from solr that was scanned longest ago, it starts with those that have no vscan timestamp'''
        
        scanned_longest_ago_or_not_scanned_dic = self.conn.search('*:*', sort='vscan_tstamp asc', rows=self.num_urls_to_scan)

        return scanned_longest_ago_or_not_scanned_dic

    def update_vscan_tstamp(self, url):

        solr_doc_pull = self.conn.search('id:' + '"' + url + '"')
        vscan_tstamp = datetime.datetime.now()

        for result in solr_doc_pull:
            result['vscan_tstamp'] = datetime.datetime.now()

        self.conn.add(solr_doc_pull)

    def delete_vscan_tstamp(self, url):

        solr_doc_pull = self.conn.search('id:' + '"' + url + '"')

        for result in solr_doc_pull:
            del result['vscan_tstamp']

        self.conn.add(solr_doc_pull)

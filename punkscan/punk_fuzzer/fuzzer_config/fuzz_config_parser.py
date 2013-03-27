# Created by Hyperion Gray, LLC
# Released under the Apache 2.0 License

import os
cwdir = os.path.dirname(__file__)
import xml.etree.ElementTree as ET
import sys
sys.path.append(cwdir)

class ConfigO:

    def __init__(self):
        self.tree = ET.parse(os.path.join(cwdir, "punk_fuzz.cfg.xml"))

    def get_xss_strings(self):

        xss_strings_elt = self.tree.findall('modules/xss_config/xss_strings/xss_string')
        xss_string_list = [xss_string.text for xss_string in xss_strings_elt]

        return xss_string_list

    def get_sqli_strings(self):

        sqli_strings_elt = self.tree.findall('modules/sqli_config/sqli_strings/sqli_string')
        sqli_string_list = [sqli_string.text for sqli_string in sqli_strings_elt]

        return sqli_string_list

    def get_bsqli_strings(self):

        bsqli_strings_elt = self.tree.findall('modules/bsqli_config/bsqli_strings/bsqli_string')
        bsqli_string_list = [bsqli_string.text for bsqli_string in bsqli_strings_elt]

        return bsqli_string_list

    def get_proxies_dic(self):

        protocol = self.tree.find('network_configs/proxy').get('type')
        ip_col_port = self.tree.find('network_configs/proxy/ip_port').text

        #return nothing if ip and port are missing in config - i.e. don't use proxy
        if not ip_col_port or not protocol:
            return {}

        #need it in this silly format to pass to requests lib
        return {protocol:ip_col_port}

    def get_solr_urls(self):

        solr_summary_url = self.tree.find('network_configs/solr/summary_url').text
        solr_details_url = self.tree.find('network_configs/solr/detail_url').text

        return {'solr_summary_url':solr_summary_url, 'solr_details_url':solr_details_url}

if __name__ == "__main__":

    print ConfigO().get_xss_strings()
    print ConfigO().get_proxies_dic()
    print ConfigO().get_sqli_strings()
    

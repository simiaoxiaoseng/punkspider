#!/usr/bin/env python
# Created by Hyperion Gray, LLC
# Released under the Apache 2.0 License

import sys
import os
import datetime
from urlparse import urlparse
cwdir = os.path.dirname(__file__)
sys.path.append(os.path.join(cwdir, "../", "pysolr/"))
sys.path.append(os.path.join(cwdir, "../", "fuzzer_config/"))
sys.path.append(cwdir)
import pysolr
import fuzz_config_parser
import traceback

class PunkMapReduceIndexer:
    '''Class to index the results of a mapreduce fuzzer job'''

    def __init__(self, domain, domain_vuln_list, reducer_instance = False, del_current = True):

        configo = fuzz_config_parser.ConfigO()
        solr_urls_dic = configo.get_solr_urls()

        solr_summary_url = solr_urls_dic['solr_summary_url']
        solr_details_url = solr_urls_dic['solr_details_url']

        self.conn_summ = pysolr.Solr(solr_summary_url, timeout = 300)
        self.conn_details = pysolr.Solr(solr_details_url, timeout = 300)

        #grab a domain entry in solr summary
        sq = 'id:' + '"' + domain + '"'
        self.solr_summary_doc = self.conn_summ.search(sq.encode("utf-8"), rows=1)
        self.domain_vuln_list = domain_vuln_list
        self.domain = domain
        self.reversed_domain = self.__reverse_url(domain)

        #use the reducer instance to set status during mapred job
        self.reducer_instance = reducer_instance

        if del_current:
            self.__clear_current()

    def __clear_current(self):
        '''Clear the solr details for the current domain. '''

        sq = 'url_main:"' + self.reversed_domain + '"'
        self.conn_details.delete(q = sq.encode("utf-8"))
        
    def __reverse_url(self, url):
        '''Reverse a url. E.g. www.google.com -> com.google.www'''

        #strip the trailing slash from the url if it has one
        last_char = url[-1]
        if last_char == "/":

            url = url[:-1]
        
        #starting with http://www.google.com
        out = urlparse(url)

        #http or https is the first element
        protocol = out.scheme.encode('utf-8')

        #www.google.com -> [www,google,com]
        url_list = out.netloc.split(".")
        url_list = [x.encode('utf-8') for x in url_list]

        #list becomes -> [com,google,www]
        url_list.reverse()

        #return com.google.www
        url_reversed = ".".encode('utf-8').join(url_list)

        return url_reversed

    def add_vuln_info(self):
        '''Index the vulnerabilities and details info'''

        vuln_details_dic_list = []        
        vuln_summary_dic = {}

        vuln_c = 0
        xss_c = 0
        sqli_c = 0
        bsqli_c = 0
        trav_c = 0
        mxi_c = 0
        xpathi_c = 0
        osci_c = 0

        #for each vulnerability, make necessary counts
        #and set necessary parameters to add to Solr

        for vuln in self.domain_vuln_list:
            
            if self.reducer_instance:
                self.reducer_instance.set_status("prepping vulnerability for indexing")
                
            vuln_details_dic = {}
            vuln_c += 1
            #get details for solr_details
            
            protocol = vuln[4]
            url_main = self.reversed_domain
            v_url = vuln[0]
            bugtype = vuln[2]
            parameter = vuln[3]
            id = self.reversed_domain + "." + str(vuln_c)

            vuln_details_dic["protocol"] = protocol
            vuln_details_dic["url_main"] = url_main
            vuln_details_dic["v_url"] = v_url
            vuln_details_dic["bugtype"] = bugtype
            vuln_details_dic["parameter"] = parameter
            vuln_details_dic["id"] = id

            vuln_details_dic_list.append(vuln_details_dic)
            
            #get the count of vulnerabilities by type
            
            if vuln[2] == "xss":
                xss_c += 1

            if vuln[2] == "sqli":
                sqli_c += 1

            if vuln[2] == "bsqli":
                bsqli_c += 1
                
            if vuln[2] == "trav":
                trav_c += 1

            if vuln[2] == "mxi":
                mxi_c += 1

            if vuln[2] == "xpathi":
                xpathi_c += 1

            if vuln[2] == "osci":
                osci_c += 1

        #commit details vulnerabilities in batch
        
        self.conn_details.add(vuln_details_dic_list)

        if self.reducer_instance:
            self.reducer_instance.set_status("adding vulnerability details")

        #set the summary details dictionary and commit
        for summ_doc in self.solr_summary_doc:

#dbg            for r in self.solr_summary_doc:
#dbg                print r

            for key, val in summ_doc.items():

                if isinstance(val, int) or key == u'id' or key == u'url':
                    continue
                
                #zero out the anchors tag (it can cause encoding issues)
                elif isinstance(val, list):
                    summ_doc[key] = []

                else:
                    try:
                        summ_doc[key] = val.encode("ascii", "ignore")
                        
                    except:
                        try:
                            summ_doc[key] = val.decode("iso-8859-1").encode("ascii", "ignore")
                        except:
                            try:
                                summ_doc[key] = val.decode("utf-8").encode("ascii", "ignore") 
                            except:
                                pass

            summ_doc["xss"] = xss_c
            summ_doc["sqli"] = sqli_c
            summ_doc["bsqli"] = bsqli_c
            summ_doc["trav"] = trav_c
            summ_doc["mxi"] = mxi_c
            summ_doc["xpathi"] = xpathi_c
            summ_doc["osci"] = osci_c
            summ_doc["vscan_tstamp"] = datetime.datetime.now()
            f = open ("/home/pgotsr/punkscan/punkscan/punk_fuzzer/fff.txt", "w")
            f.write(str(summ_doc))


            
        if self.reducer_instance:
            self.reducer_instance.set_status("adding vulnerability summary")

        try:
            print self.solr_summary_doc
            self.conn_summ.add(self.solr_summary_doc)
        except:
            print "indexing failed:"
            for r in self.solr_summary_doc:
                print r
            print traceback.format_exc()

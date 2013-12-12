#!/usr/bin/python
import sys
from datetime import datetime
import time
import requests
import json
from ConfigParser import ConfigParser
conf = ConfigParser()
conf.read("punkcrawler.cfg")
from pnk_logging import pnk_log
mod = __file__

def mapper():
    
    headers = {"content-type" : "application/json"}
    for line in sys.stdin:

        domain = line.split("\t")[1].strip()
        solr_update_json = build_solr_update(domain)

        pnk_log(mod, "Sending json: %s" % solr_update_json)
        solr_summ_url = conf.get("punkcrawler", "solr_summary_url")
        
        pnk_log(mod, "Indexing %s to Solr"% domain)
        r = requests.post(solr_summ_url, data = solr_update_json, headers = headers)

    pnk_log(mod, "Finished a round of indexing")

def build_solr_update(domain):
    """Perform a partial update on url and tstamp in solr. Prevents docs from being overwritten."""

    if not domain.endswith("/"):
        domain = domain + "/"

    return json.dumps([{"id" : domain, "url" : {"set" : domain}, "tstamp"  : {"set" : str(datetime.now().isoformat() + "Z")}}])

def commit():

    solr_summ_url = conf.get("punkcrawler", "solr_summary_url")
    commit_url = solr_summ_url + "?commit=true"

    headers = {"content-type" : "application/json", "content-length" : 0}
    r = requests.post(commit_url, headers = headers)
    pnk_log(mod, "Committing to solr with URL %s" % commit_url)
    pnk_log(mod, "Server returned response %s" % str(r.status_code))
    print r.text

if __name__ == "__main__":
    
    try:   
        if sys.argv[1] == "--commit":
            commit()
        else:
            mapper()
            
    except:
        mapper()
        

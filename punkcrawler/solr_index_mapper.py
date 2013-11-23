import sys
from datetime import datetime
import requests
import json
from ConfigParser import ConfigParser
conf = ConfigParser()
conf.read("punkcrawler.cfg")

def mapper():
    
    headers = {"content-type" : "application/json"}
    for line in sys.stdin:
        
        domain = line.split("\t")[0].strip()
        solr_update_json = build_solr_update(domain)
        solr_summ_url = conf.get("punkcrawler", "solr_summary_url")
        r = requests.post(solr_summ_url, data = solr_update_json, headers = headers)

    sys.stderr.write("Finished a round of indexing")

def build_solr_update(domain):
    """Perform a partial update on url and tstamp in solr. Prevents docs from being overwritten. """

    if not domain.endswith("/"):
        domain = domain + "/"

    return json.dumps({"id" : domain, "url" : {"set" : domain}, "tstamp"  : {"set" : datetime.now()}})        
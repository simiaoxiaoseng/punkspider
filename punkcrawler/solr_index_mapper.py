#!/usr/bin/python
import sys
from datetime import datetime
import zipimport
importer_bs4 = zipimport.zipimporter("lib/bs4.zip")
bs4 = importer_bs4.load_module("bs4")

from bs4 import BeautifulSoup, SoupStrainer
import time
import requests
import json
from urlparse import urlparse
from ConfigParser import ConfigParser
conf = ConfigParser()
conf.read("punkcrawler.cfg")
from pnk_logging import pnk_log
mod = __file__
from pnk_requests import pnk_request


def mapper():
    
    headers = {"content-type" : "application/json"}
    for line in sys.stdin:

        domain_page = line.split("\t")[1].strip()
        solr_update_json = build_solr_update(domain_page)

        pnk_log(mod, "Sending json: %s" % solr_update_json)
        solr_summ_url = conf.get("punkcrawler", "solr_summary_url")
        
        pnk_log(mod, "Indexing %s to Solr"% domain_page)
        r = requests.post(solr_summ_url, data = solr_update_json, headers = headers, proxy = get_index_proxy())

    pnk_log(mod, "Finished a round of indexing")

def build_solr_update(domain_page):
    """Perform a partial update on url and tstamp in solr. Prevents docs from being overwritten."""

    if not domain_page.endswith("/"):
        domain_page = domain_page + "/"

    title = resolve_title(domain_page)
    return json.dumps([{"id" : domain_page, "title" : {"set" : title}, "url" : {"set" : domain_page}, "tstamp"  : {"set" : str(datetime.now().isoformat() + "Z")}}])

def resolve_title(url):

    #grab the first title if there's more than one
    try:
        pnk_log(mod, "Requesting %s" % url)
        r = pnk_request(url)
        response_text = r.text
        
        for title in BeautifulSoup(response_text, 'html.parser', parse_only=SoupStrainer('title')):
            return title.text.strip()
    except:
        return None

def commit():

    solr_summ_url = conf.get("punkcrawler", "solr_summary_url")
    commit_url = solr_summ_url + "?commit=true"

    headers = {"content-type" : "application/json", "content-length" : 0}
    r = requests.post(commit_url, headers = headers, proxy = get_index_proxy())
    pnk_log(mod, "Committing to solr with URL %s" % commit_url)
    pnk_log(mod, "Server returned response %s" % str(r.status_code))
    print r.text

def get_index_proxy():
    purl = urlparse(conf.get("punkcrawler", "index_proxy"))
    return {purl.scheme : purl.netloc}

if __name__ == "__main__":
    
    try:   
        if sys.argv[1] == "--commit":
            commit()
        else:
            mapper()
            
    except:
        mapper()
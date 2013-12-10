#!/usr/bin/python
import zipimport

importer_requests = zipimport.zipimporter("lib/requests.zip")
bs4 = importer_requests.load_module("requests")

import requests
from ConfigParser import ConfigParser
from urlparse import urlparse
conf = ConfigParser()
conf.read("punkcrawler.cfg")

def get_proxy():
    purl = urlparse(conf.get("punkcrawler", "proxy"))
    return {purl.scheme : purl.netloc}    
    
def pnk_request(url):
    r = requests.get(url, proxies=get_proxy(), timeout=int(conf.get("punkcrawler", "timeout")))
    return r

def pnk_head(url):
    r = requests.head(url, proxies=get_proxy(), timeout=int(conf.get("punkcrawler", "timeout")))
    return r

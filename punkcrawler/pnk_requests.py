#!/usr/bin/python
import zipimport
import traceback

from multiprocessing import TimeoutError
from multiprocessing.pool import ThreadPool

importer_requests = zipimport.zipimporter("lib/requests.zip")
bs4 = importer_requests.load_module("requests")

import requests
from requests.exceptions import ConnectionError
from ConfigParser import ConfigParser
from urlparse import urlparse
from pnk_logging import pnk_log
mod = __file__
conf = ConfigParser()
conf.read("punkcrawler.cfg")

def get_proxy():
    purl = urlparse(conf.get("punkcrawler", "proxy"))
    return {purl.scheme : purl.netloc}

def pnk_request_raw(url):
    r = requests.get(url, proxies=get_proxy(), timeout=int(conf.get("punkcrawler", "timeout")))
    return r

def pnk_request(url):

    pool = ThreadPool(processes = 1)
    async_result = pool.apply_async(pnk_request_raw, (url,))

    try:
        ret_val = async_result.get(timeout = int(conf.get("punkcrawler", "hard_timeout")))
    except TimeoutError as te:
        traceback.print_exc()
        pnk_log(mod, "Received hard timeout, raising timeout exception")
        #raise requests ConnectionError for easier handling if there's a hard timeout
        raise ConnectionError("Request received a hard timeout")

    return ret_val

def pnk_head(url):
    r = requests.head(url, proxies=get_proxy(), timeout=int(conf.get("punkcrawler", "timeout")))
    return r
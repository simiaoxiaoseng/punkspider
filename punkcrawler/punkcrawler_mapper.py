from bs4 import BeautifulSoup, SoupStrainer
import sys
from urlparse import urlparse, urlunparse
import traceback
from pnk_requests import pnk_request
from ConfigParser import ConfigParser
conf = ConfigParser()
conf.read("punkcrawler.cfg")

def mapper():
    
    #!should go in config file
    max_links = int(conf.get("punkcrawler", "max_links_per_url"))
    for line in sys.stdin:
        
        domain, urlin_clean = line.split("\t")
        domain = domain.strip()
        urlin_clean = urlin_clean.strip()
        
        try:
            r = pnk_request(urlin_clean)
            response_text = r.text

            link_c = 0
            for link in BeautifulSoup(response_text, 'html.parser', parse_only=SoupStrainer('a')):
                
                if link_c > max_links:
                    break

                href = link.get('href')
                
                if href and not href.startswith("mailto:"):

                    #print newfound URLs
                    print get_host(normalize_url(normalize_link(href, urlin_clean))) + "\t" + normalize_url(normalize_link(href, urlin_clean))
                    
                link_c = link_c + 1

        except:
            traceback.print_exc()

        #if something goes wrong, just print url
        print get_host(normalize_url(urlin_clean)) + "\t" + normalize_url(urlin_clean)
                                                            
def normalize_link(url_to_normalize, current_page_url):

    cp_parsed = urlparse(current_page_url)
    cp_scheme = cp_parsed.scheme
    cp_netloc = cp_parsed.netloc
    
    parsed_url_to_normalize = urlparse(url_to_normalize)

    scheme, netloc, path, params, query, fragment = urlparse(url_to_normalize)
    
    if not parsed_url_to_normalize.scheme or not parsed_url_to_normalize.netloc:
        
        full_url = urlunparse((cp_scheme, cp_netloc, path, params, query, fragment))        
    else:
        full_url = urlunparse(parsed_url_to_normalize)
        
    return full_url

def get_host(url):
    
    return urlparse(url).netloc.split(":")[0]

def normalize_url(url):
        
    if url[-1] == "/":
        url = url[:-1]

    return url
    
if __name__ == "__main__":
    
    mapper()    
from bs4 import BeautifulSoup, SoupStrainer
import requests
import sys
from urlparse import urlparse, urlunparse

def mapper():
    
    for urlin in sys.stdin:
        try:
            urlin_clean = urlin.strip()
            print normalize_url(urlin_clean)
            r = requests.get(urlin_clean)
            response_text = r.text
            for link in BeautifulSoup(response_text, 'html.parser', parse_only=SoupStrainer('a')):
                href = link.get('href')
                if href and not href.startswith("mailto:"):
                    
                    print normalize_url(normalize_link(href, urlin_clean))

        except:
            
            print normalize_url(urlin_clean)
            
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

def normalize_url(url):
        
    if url[-1] == "/":
        url = url[:-1]

    return url
    
if __name__ == "__main__":
    
    mapper()    
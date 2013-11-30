import sys
from pnk_requests import pnk_head
import traceback
from requests import Timeout
from requests import HTTPError
from requests import ConnectionError
from pnk_logging import pnk_log
from urlparse import urlparse

def mapper():
    #purge 404s in urls.txt
    
    mod = __file__
    for line in sys.stdin:

        try:
            domain, urlin_clean = line.split("\t")
            domain = domain.strip()
            urlin_clean = urlin_clean.strip()

        except:
            pnk_log(mod, "Bad line in file: %s" % line)
            continue
        
        try:
            netloc = urlparse(urlin_clean).netloc
            if "." not in netloc:
                #!Not sure if I like this, but it's a nice offline check
                pnk_log(mod, "URL %s does not have a dot in it, i.e. no domain specified, skipping it" % urlin_clean)
                continue
                
        except:
            continue
        
        try:
            pnk_log(mod, "Requesting %s" % urlin_clean)
            r = pnk_head(urlin_clean)
            if r.status_code != 404:
                print domain + "\t" + urlin_clean

        except Timeout:
            pnk_log(mod, "Timeout, assuming invalid URL")
            print domain + "\t" + urlin_clean
            traceback.print_exc()

        except ConnectionError:
            #this is raised if connection drops, in which case
            #just assume URLs are valid
            pnk_log(mod, "Connection error, assuming valid URL")
            print domain + "\t" + urlin_clean
            traceback.print_exc()

        except HTTPError:
            #if there's an HTTP type exception
            pnk_log(mod, "HTTP protocol error, assuming invalid URL")
            traceback.print_exc()
        
        except KeyboardInterrupt:
            pnk_log(mod, "PunkCRAWLER killed by user")
            sys.exit(1)

        except:
            pnk_log(mod, "Generic error, assuming invalid URL")
            traceback.print_exc()

if __name__ == "__main__":

    mapper()
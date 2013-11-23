import sys
from pnk_requests import pnk_request

def mapper():
    #purge 404s in urls.txt
    
    for line in sys.stdin:
        domain, urlin_clean = line.split("\t")
        domain = domain.strip()
        urlin_clean = urlin_clean.strip()
        
        try:
            r = pnk_request(urlin_clean)
            if r.status_code != 404:
                print domain + "\t" + urlin_clean            

        except:
            
            print domain + "\t" + urlin_clean

if __name__ == "__main__":
    mapper()
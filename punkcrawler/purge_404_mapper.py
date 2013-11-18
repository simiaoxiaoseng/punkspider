import sys
import requests

def mapper():
    #purge 404s in urls.txt
    
    for urlin in sys.stdin:
        urlin_clean = urlin.strip()
        try:
            urlin_clean = urlin.strip()
            r = requests.get(urlin_clean)
            if r.status_code != 404:
                print urlin_clean            

        except:
            
            print urlin_clean

if __name__ == "__main__":
    mapper()    
import sys
from urlparse import urlparse

def mapper():
    
    for line in sys.stdin:
        try:
            url = line.strip()
            host = urlparse(url).netloc.split(":")[0]
            print host + "\t" + url

        except:
            #safe to print exception to stderr?
            pass
        
if __name__=="__main__":
    
    mapper()
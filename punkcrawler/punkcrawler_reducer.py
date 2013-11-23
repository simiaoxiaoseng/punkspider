import sys

current_domain = None

for line in sys.stdin:
    
    domain, url = line.split("\t")
    domain = domain.strip()
    
    if current_domain == domain:
        pass
    else:
        print domain + "\t" + "http://" + domain
        current_domain = domain

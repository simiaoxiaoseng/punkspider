import pysolr
from random import randrange

conn = pysolr.Solr('http://cloud-solr:8983/solr/')

results = conn.search("title:china")

for result in results:

	nxss = randrange(10)
	nsqli = randrange(10)
	nbsqli = randrange(10)
	result['xss'] = nxss
	result['sqli'] = nsqli
	result['bsqli'] = nbsqli

conn.add(results)
	

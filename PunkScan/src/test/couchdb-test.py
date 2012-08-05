from couchdb import Server
from couchdb.client import Server, Document
from couchdb.mapping import TextField, DateTimeField, ListField, DictField
import datetime

server = Server('http://localhost:5984')
print server

try:
        db = server['test2']
except Exception:
        db = server.create('test2')
 
print db

class Vulns(Document):

	_id = TextField()
	url = TextField()
	vulnis = ListField(DictField())
	added = DateTimeField(default=datetime.datetime.now())
	xss = ListField(DictField())
	sqli = ListField(DictField())
	bsqli = ListField(DictField())

sqli_list = []
bsqli_list = []
xss_list = [{'url': 'http://localhost/index2.php?age=%3Cscript%3Ealert%28%27e4nqezp5vc%27%29%3C%2Fscript%3E&name=on', 'info': 'XSS (age2)',\
'parameter': 'age=%3Cscript%3Ealert%28%27e4nqezp5vc%27%29%3C%2Fscript%3E&name=on', 'level': '1'}, {'url': 'http://localhost/index.php?age=on&name=%3Cscript%3Ealert%28%272udr67frn0%27%29%3C%2Fscript%3E', 'info': 'XSS (name)',\
'parameter': 'age=on&name=%3Cscript%3Ealert%28%272udr67frn0%27%29%3C%2Fscript%3E', 'level': '1'}, {'url':"http://whw", 'info':'XSS', 'paramter':'whatevawefawefwaefer...'}]


try:
	vulns = Vulns(_id = "http://localhost3", url = 'http://localhost3', xss = xss_list, bsqli = bsqli_list, sqli = sqli_list)
	db.save(vulns)

except:
#reference a document with ID 
	doc = db['http://localhost3']

#Update document field
	doc['xss'] = xss_list
	db.save(doc)

#docid="http://localhost"

#doc = ''

#for docs in db:
#	doc = db.get(docid)

#doc['url'] = "ewfaw"


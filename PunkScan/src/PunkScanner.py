#PunkScanner is a module that sits on top of Wapiti, handles threading etc., and indexes these results to couchdb and Solr
import sys
import traceback
sys.path.append('wapiti-2.2.1/src/')
sys.path.append('pysolr/')
sys.path.append('xmltodict/')
sys.path.append('couchdb/')
import wapiti
import pysolr
import datetime
from lxml import etree
from couchdb import Server
from couchdb.client import Server, Document
from couchdb.mapping import TextField, DateTimeField, ListField, DictField
import subprocess

class ParserUploader:
	'''This class takes in a wapiti XML report (usually from a Target object) and uploads it to couchdb'''

	def __init__(self, report, url):
		'''At init, get the sql injectin bugs, xss bugs, and exec bugs. Also have lxml take in the wapiti report given to it.'''

		self.doc = etree.fromstring(report)
		self.url = url
                self.__get_sql()
                self.__get_xss()
                self.__get_bsql()

	def __get_sql(self):
		'''Gets the sql injection bugs'''

                sql_bugs = self.doc.xpath("bugTypeList/bugType[@name='SQL Injection']/bugList/bug")
		sql_bugs_dic_list = []

		if sql_bugs:

			for bug in sql_bugs:

				sql_bug_dic = {}
				sql_bug_dic["level"] = bug.get("level")
				sql_bug_dic["url"] = bug.find("url").text.strip()
				sql_bug_dic["parameter"] = bug.find("parameter").text.strip()
				sql_bug_dic["info"] = bug.find("info").text.strip()
				sql_bugs_dic_list.append(sql_bug_dic)

		self.sql_bugs_dic_list = sql_bugs_dic_list

	def __get_xss(self):
		'''Gets the xss bugs'''

                xss_bugs = self.doc.xpath("bugTypeList/bugType[@name='Cross Site Scripting']/bugList/bug")
                xss_bugs_dic_list = []

                if xss_bugs:

                        for bug in xss_bugs:

                                xss_bug_dic = {}
                                xss_bug_dic["level"] = bug.get("level")
                                xss_bug_dic["url"] = bug.find("url").text.strip()
                                xss_bug_dic["parameter"] = bug.find("parameter").text.strip()
                                xss_bug_dic["info"] = bug.find("info").text.strip()
                                xss_bugs_dic_list.append(xss_bug_dic)

                self.xss_bugs_dic_list = xss_bugs_dic_list

        def __get_bsql(self):
                '''Gets the bsql bugs'''

                bsql_bugs = self.doc.xpath("bugTypeList/bugType[@name='Blind SQL Injection']/bugList/bug")
                bsql_bugs_dic_list = []

                if bsql_bugs:

                        for bug in bsql_bugs:

                                bsql_bug_dic = {}
                                bsql_bug_dic["level"] = bug.get("level")
                                bsql_bug_dic["url"] = bug.find("url").text.strip()
                                bsql_bug_dic["parameter"] = bug.find("parameter").text.strip()
                                bsql_bug_dic["info"] = bug.find("info").text.strip()
                                bsql_bugs_dic_list.append(bsql_bug_dic)

                self.bsql_bugs_dic_list = bsql_bugs_dic_list

	def __get_exec(self):
		'''Gets the command execution bugs'''
	
                exec_bugs = self.doc.xpath("bugTypeList/bugType[@name='Commands execution']/bugList/bug")
                exec_bugs_dic_list = []

                if exec_bugs:

                        for bug in exec_bugs:

                                exec_bug_dic = {}
                                exec_bug_dic["level"] = bug.get("level")
                                exec_bug_dic["url"] = bug.find("url").text.strip()
                                exec_bug_dic["parameter"] = bug.find("parameter").text.strip()
                                exec_bug_dic["info"] = bug.find("info").text.strip()
                                exec_bugs_dic_list.append(exec_bug_dic)

                self.exec_bugs_dic_list = exec_bugs_dic_list

	def solr_update(self, n_xss, n_sql, n_bsql):

		conn = pysolr.Solr('http://hg-solr:8080/solr/')
		solr_doc_pull = conn.search("id:" + " \"" + self.url + "\" ")
		vscan_tstamp = datetime.datetime.now()

		for result in solr_doc_pull:
			result["xss"] = n_xss
			result["sqli"] = n_sql
			result["bsqli"] = n_bsql
			result["vscan_tstamp"] = datetime.datetime.now()

		conn.add(solr_doc_pull)

	def scdb_index(self):
		'''This indexes vulnerabilities to couchdb and updates the timestamp and number of vulns in solr'''

		#! change connection string in production
		server = Server('http://hg-couchdb:5984')

		#! set db name for production
		try:
        		db = server['vulnerabilities']
		except Exception:
        		db = server.create('vulnerabilities')

		class Vulns(Document):

		        _id = TextField()
        		url = TextField()
        		vulnis = ListField(DictField())
        		added = DateTimeField(default=datetime.datetime.now())
        		xss = ListField(DictField())
        		sqli = ListField(DictField())
        		bsqli = ListField(DictField())
#!        		execu = ListField(DictField())

		try:

			vulns = Vulns(_id = self.url, url = self.url, xss = self.xss_bugs_dic_list, sqli = self.sql_bugs_dic_list, bsqli = self.bsql_bugs_dic_list)
			db.save(vulns)
			print "Saved a new doc"

		except:

			couch_doc = db[self.url]
			couch_doc['xss'] = self.xss_bugs_dic_list
			couch_doc['sqli'] = self.sql_bugs_dic_list
			couch_doc['bsqli'] = self.bsql_bugs_dic_list
#!			couch_doc['execu'] = self.exec_bugs_dic_list
			db.save(couch_doc)
			print "Updated a doc"

		print "Updating Solr..."
		self.solr_update(len(self.xss_bugs_dic_list), len(self.sql_bugs_dic_list), len(self.bsql_bugs_dic_list))

class PunkSolr():
	'''This class pulls URLs from solr in a variety of ways for later scanning'''

	def __init__(self):

                self.conn = pysolr.Solr("http://hg-solr:8080/solr/")

	def get_not_scanned(self):
		'''get solr records with no vscan timestamp'''
		self.not_scanned = self.conn.search("-vscan_tstamp:*", rows=1)

		return self.not_scanned

	def get_scanned_longest_ago(self):
		'''This gets the record from solr that was scanned longest ago, it starts with those that have no vscan timestamp'''
		scanned_longest_ago_or_not_scanned = self.conn.search('*:*', sort='vscan_tstamp asc', rows=1)
		
		return scanned_longest_ago_or_not_scanned

class Target():
	'''This class holds a target object and performs the actual scan. Once a scan is performed the result is a wapiti XML report'''

	def __init__(self):

		self.punk_solr = PunkSolr()
		self.timestamp = datetime.datetime.now()
#		self.seturl(self, url, "out.xml")

	def set_url(self, url, outfile):

		self.url = url
		self.opt_list = [('-o', outfile), ('-f', 'xml'), ('-b', 'domain'), ('-v', '2'), ('-u', ''), ('-n', '1'), ('-t', '5'),\
#!		('-m', '-all,xss:get,sql:get,blindsql:get')]
		('-m', '-all,sql:get')]
		

	def update_vscan_tstamp(self):

                conn = pysolr.Solr('http://hg-solr:8080/solr/')
                solr_doc_pull = conn.search("id:" + " \"" + self.url + "\" ")
                vscan_tstamp = datetime.datetime.now()

                for result in solr_doc_pull:
                        result["vscan_tstamp"] = datetime.datetime.now()

                conn.add(solr_doc_pull)

	def delete_vscan_tstamp(self):

                conn = pysolr.Solr('http://hg-solr:8080/solr/')
                solr_doc_pull = conn.search("id:" + " \"" + self.url + "\" ")

                for result in solr_doc_pull:
                        del result["vscan_tstamp"]

                conn.add(solr_doc_pull)

	def punk_scan(self):
		'''This performs the actual scan. Note that the timestamp is updated before the scan starts, this makes it such that other scanners
		know this is being scanned before it finishes the scanning. Reduces number of duplicate scans'''

		wap = wapiti.Wapiti(self.url)		
		return wap.scan(self.url, self.opt_list)

if __name__ == "__main__":

	total_time_sec = 0
	sites_scanned = 0

	while True:

		start_scan = datetime.datetime.now()
		print "\n\n***getting a new website to scan***\n\n"
		try:
			site_to_scan = PunkSolr().get_scanned_longest_ago() 
		except Exception, err:
			traceback.print_exc(file=sys.stdout)
			print "Could not get site to scan, trying again"
			continue

		for website_dic in site_to_scan:

			print "Retrieved solr document:"
			print website_dic
			print "___________________\n"

			target = Target()
			target.set_url(website_dic['url'], 'out.xml')

			try:
				target.update_vscan_tstamp()
			except Exception, err:
				traceback.print_exc(file=sys.stdout)
				print "Could not update vulnerability time stamp in solr, trying again"
				continue

			try:
				scan_result = target.punk_scan()
			except Exception, err:

				traceback.print_exc(file=sys.stdout)
				print "Error while scanning, attempting to delete timestamp"
				try:
					target.delete_vscan_tstamp()
				except Exception, err:
					traceback.print_exc(file=sys.stdout)
					print "Error while attempting to delete timestamp, waiting 5 seconds, trying again and restarting the loop"
					time.sleep(5)
					try:
						target.delete_vscan_tstamp()					
					except Exception, err:
						traceback.print_exc(file=sys.stdout)
						print "Deleting timestamp failed again. You may have corrupted data in Solr."
						continue

			scan_url = target.url

			try:
				ParserUploader(scan_result, scan_url).scdb_index()
			except Exception, err:
				traceback.print_exc(file=sys.stdout)
				print "Uploading of Solr document failed. Trying again."
				try:
					ParserUploader(scan_result, scan_url).scdb_index()
				except Exception, err:
					traceback.print_exc(file=sys.stdout)
					print "Uploading results to solr failed again. Attempting to delete timestamp"
					try:
						target.delete_vscan_tstamp()
					except Exception, err:
						traceback.print_exc(file=sys.stdout)
						print "Deleting timestamp failed, sleeping 5 seconds and trying again."
						time.sleep(5)
						try:
							target.delete_vscan_tstamp()				
						except Exception, err:
							traceback.print_exc(file=sys.stdout)
							print "Deleting timestamp failed again, you may have corrupt data in Solr. Moving on."
							continue

			end_scan = datetime.datetime.now()
			scan_time_delta = end_scan - start_scan
			scan_time_sec = scan_time_delta.total_seconds()
			scan_time = scan_time_sec/60

			print "Scan took %s minutes to run." % str(scan_time)
			sites_scanned = sites_scanned + 1
			total_time_sec = total_time_sec + scan_time_sec
			total_time = total_time_sec/86400
			avg_rate = sites_scanned/total_time

			print "%s sites scanned so far. That's a rate of %s sites per day" % (str(sites_scanned), str(avg_rate))

import sys
import os
cwdir = os.path.dirname(__file__)
punkscan_base = os.path.join(cwdir, "../")
sys.path.append(os.path.join(punkscan_base,"pysolr/"))
sys.path.append(os.path.join(punkscan_base, 'hadooper'))
import hadooper
import pysolr
from ConfigParser import SafeConfigParser
config_parser = SafeConfigParser()
config_parser.read(os.path.join(punkscan_base,'punkscan_configs', 'punkscan_config.cfg'))
HADOOP_HOME=config_parser.get('directories','HADOOP_HOME')
NUTCH_HOME=config_parser.get('directories','NUTCH_HOME')
NUTCH_RUNTIME_DEP = os.path.join(NUTCH_HOME, "runtime", "deploy")

class ConfigoRoboto:
	'''This class is in charge of replacing and writing configuration files for nutch and/or hadoop'''

        def __init__(self):

                self.conn = pysolr.Solr("http://hg-solr:8080/solr/summary/")
		self.num_urls_to_scan = config_parser.get('performance','sim_urls_to_scan')

        def __get_scanned_longest_ago(self):
                '''This gets the record from solr that was scanned longest ago, it starts with those that have no vscan timestamp'''
                scanned_longest_ago_or_not_scanned_dic = self.conn.search('*:*', sort='vscan_tstamp asc', rows=self.num_urls_to_scan)

                return scanned_longest_ago_or_not_scanned_dic

	def __get_regex_url(self, no_regex = False):
		'''Replace regex url configuration file, this will be used by punkscan to restrict crawls to the domains we are going to scan'''
		#sample regex: +https?://www.leavenworth.org/.*

		solr_urls_dic = self.__get_scanned_longest_ago()

		for url_dic in solr_urls_dic:
			if not no_regex:
				url_regex = "+" + url_dic['url'].rstrip("/") + ".*"
				yield url_regex
			else:
				yield url_dic['url']

	def generate_template_file(self):

		f_template = open(os.path.join(os.path.dirname(__file__),"templates","regex-urlfilter.txt"),'r').read()
		for url_regex in self.__get_regex_url():
			f_template += url_regex + "\n"

		f_final = open(os.path.join(HADOOP_HOME,'conf','regex-urlfilter.txt'),'w').write(f_template)

	def generate_seed_list(self):

		f_seed = open(os.path.join(NUTCH_HOME, "runtime", "deploy", "urls", "seed.txt"),'w')

		for url in self.__get_regex_url(no_regex = True):
			url_n = url + "\n"
			f_seed.write(url_n)

	def clear_and_put_seed_list_on_hdfs(self):
	
		hadooper.Hadooper().rmr("urls")
		hadooper.Hadooper().copyFromLocal(os.path.join(NUTCH_RUNTIME_DEP, "urls"), "urls")
		


if __name__ == "__main__":

	x = ConfigoRoboto()
#	x.generate_template_file()
#	x.generate_seed_list()
	x.clear_and_put_seed_list_on_hdfs()	

import sys
import os
cwdir = os.path.dirname(__file__)
punkscan_base = os.path.join(cwdir, "../")
sys.path.append(os.path.join(punkscan_base,"punk_solr"))
sys.path.append(os.path.join(punkscan_base, 'hadooper'))
import hadooper
import punkscan_solr
from ConfigParser import SafeConfigParser
config_parser = SafeConfigParser()
config_parser.read(os.path.join(punkscan_base,'punkscan_configs', 'punkscan_config.cfg'))
HADOOP_HOME=config_parser.get('directories','HADOOP_HOME')
NUTCH_HOME=config_parser.get('directories','NUTCH_HOME')
NUTCH_RUNTIME_DEP = os.path.join(NUTCH_HOME, "runtime", "deploy")

class ConfigoRoboto:
	'''This class is in charge of replacing and writing configuration files for nutch and/or hadoop'''

        def __init__(self):

		self.punk_solro = punkscan_solr.PunkSolr()
		self.solr_urls_dic = self.punk_solro.get_scanned_longest_ago()

	def __get_regex_url(self, no_regex = False):
		'''Replace regex url configuration file, this will be used by punkscan to restrict crawls to the domains we are going to scan.
		This method is very important. As soon as this method is called, a URL is marked as being scanned in Solr'''

		#sample regex entry: +http://www.leavenworth.org/.*

		for url_dic in self.solr_urls_dic:

			#mark the url as being scanned with the vscan_tstamp field
			self.punk_solro.update_vscan_tstamp(url_dic['url'])
			
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

		seed_dir = os.path.join(NUTCH_HOME, "runtime", "deploy", "urls")

		if not os.path.exists(seed_dir):
			os.makedirs(seed_dir)

		f_seed = open(os.path.join(seed_dir, "seed.txt"),'w')

		for url in self.__get_regex_url(no_regex = True):
			url_n = url + "\n"
			f_seed.write(url_n)

	def clear_and_put_seed_list_on_hdfs(self):
	
		hadooper.Hadooper().rmr("urls")
		hadooper.Hadooper().copyFromLocal(os.path.join(NUTCH_RUNTIME_DEP, "urls"), "urls")

if __name__ == "__main__":

	x = ConfigoRoboto()
	x.generate_template_file()
	x.generate_seed_list()
	x.clear_and_put_seed_list_on_hdfs()	

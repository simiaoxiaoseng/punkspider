import sys
import os
cwdir = os.path.dirname(__file__)
punkscan_base = os.path.join(cwdir, "../")
sys.path.append(os.path.join(punkscan_base,"punk_solr"))
sys.path.append(os.path.join(punkscan_base, 'hadooper'))
sys.path.append(cwdir)
import hadooper
import punkscan_solr
from ConfigParser import SafeConfigParser
import paramiko
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
	    self.datanodes = config_parser.get('hadoop', 'datanodes').split(',')
	    self.urlfilter_lcp = os.path.join(HADOOP_HOME,'conf','regex-urlfilter.txt')
	    self.username = config_parser.get('users', 'hadoop_user')

	def __get_regex_url(self, no_regex = False):
		'''Replace regex url configuration file, this will be used by punkscan to restrict crawls to the domains we are going to scan.
		This method is very important. As soon as this method is called, a URL is marked as being scanned in Solr'''

        #sample regex entry: +http://www.leavenworth.org/.*

	    for url_dic in self.solr_urls_dic:

            #mark the url as being scanned with the vscan_tstamp field
	        self.punk_solro.update_vscan_tstamp(url_dic['url'])
			
		if not no_regex:
		    url_regex = "+" + url_dic['url'] + ".*"
		    yield url_regex

		else:
		    yield url_dic['url']

	def __transfer_sftp(self, host_raw, local_path, remote_path):
		'''Transfer file via SFTP '''

	    host = "".join(host_raw.split())
	    ssh = paramiko.SSHClient()
	    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	    ssh.connect(host)
	    sftp=ssh.open_sftp()
	    sftp.put(local_path, remote_path)

	def __transfer_urlfilter(self):
		'''Transfer the regex-urlfilter.txt file to each datanode '''

	    failed_node_num = 0
		failed_node_list = []
	    for node in self.datanodes:

	        print "Transferring urlfilter file to %s" % node
	
			try:
			    self.__transfer_sftp(node, self.urlfilter_lcp, self.urlfilter_lcp)

			except:
				print "Failed to transfer urlfilter-regex.txt to %s" % node
			    failed_node_num = failed_node_nums + 1
		
		print "Failed to transfer regex-urlfilter.txt to %s nodes. If these nodes\
		come back up this may cause unexpected results." % str(failed_node_num)

	def generate_template_file(self):

		f_template = open(os.path.join(os.path.dirname(__file__),"templates","regex-urlfilter.txt"),'r').read()
		for url_regex in self.__get_regex_url():
			f_template += url_regex + "\n"

		f_final = open(self.urlfilter_lcp, 'w').write(f_template)

		#transfer urlfilter config to each datanode to override nutch config
		if self.datanodes[0]:
			self.__transfer_urlfilter()

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

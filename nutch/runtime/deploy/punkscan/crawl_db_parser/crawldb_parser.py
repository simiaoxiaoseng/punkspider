import sys
import os
import subprocess
import shutil
cwdir = os.path.dirname(__file__)
print cwdir
punkscan_base = os.path.join(cwdir, "../")
sys.path.append(os.path.join(punkscan_base, 'hadooper'))
import hadooper
from ConfigParser import SafeConfigParser
import csv
import glob
config_parser = SafeConfigParser()
config_parser.read(os.path.join(punkscan_base,'punkscan_configs', 'punkscan_config.cfg'))
HADOOP_HOME=config_parser.get('directories','HADOOP_HOME')
NUTCH_HOME=config_parser.get('directories','NUTCH_HOME')
NUTCH_RUNTIME_DEP = os.path.join(NUTCH_HOME, "runtime", "deploy")

class CrawlDBParser:

    def __init__(self):

        pass

    def dump_crawl_db(self):

        #clear current crawl dump if exists
        hadooper.Hadooper().rmr('punkscan_crawl_dump')

        nutch_bin = os.path.join('bin','nutch')

        #would have used webhdfs but does not have moveFromLocal function
        #this function is the most efficient way, as then we will not have to delete the crawldb once done

        shell_call_list = [nutch_bin, 'readdb', os.path.join('punkscan_crawl', 'crawldb'), '-dump', 'punkscan_crawl_dump', '-format', 'csv']
	    	
	output = subprocess.Popen(shell_call_list, cwd = NUTCH_RUNTIME_DEP).communicate()[0]

    def get_crawl_db_dump(self):

	try:
            shutil.rmtree(os.path.join(NUTCH_RUNTIME_DEP, 'punkscan_crawl_dump'))

	except:
            print "problem deleting directory, perhaps it doesn't exist yet?"
            pass

        hadooper.Hadooper().copyToLocal('punkscan_crawl_dump', os.path.join(NUTCH_RUNTIME_DEP, 'punkscan_crawl_dump'))

    def crawl_db_url_generator(self):
        '''Generator for the urls from the crawldb  '''

        crawl_db_files = glob.glob(os.path.join(NUTCH_RUNTIME_DEP, "punkscan_crawl_dump", "*"))

        for crawl_db_file in crawl_db_files:
	    crawl_db_csv = open(crawl_db_file, "rb")
	    crawl_db_read = csv.DictReader(crawl_db_csv, delimiter = ";", quotechar='"')

	    for row in crawl_db_read:
	        yield row["Url"]
		
if __name__ == "__main__":

    x = CrawlDBParser()
    x.dump_crawl_db()
    x.get_crawl_db_dump()
    for whatever in x.crawl_db_url_generator():
        print whatever

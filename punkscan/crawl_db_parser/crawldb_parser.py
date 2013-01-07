import sys
import os
import subprocess
import shutil
cwdir = os.path.dirname(__file__)
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
import re

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


    def __skip_ascii_null(self, csv_data):

        for line in csv_data:

            try:

                yield line

            except:

                pass

    def crawl_db_url_generator(self):
        '''Generator for the urls from the crawldb'''

        crawl_db_files = glob.glob(os.path.join(NUTCH_RUNTIME_DEP, "punkscan_crawl_dump", "*"))
        trouble_list = []
        for crawl_db_file in crawl_db_files:

            crawl_db = open(crawl_db_file, "r")
            iterfile = iter(crawl_db)
            next(iterfile)

            for line in iterfile:

                #we use regular expressions because of the encoding deficiencies in the csv module
                m = re.match(r'\"(.*)\";(.*);(.*);(.*);(.*);(.*);(.*);(.*);(.*);', line)

                if m:
                    result = m.group(1)
                else:
                    trouble_list.append(line)

                yield result
        
        print "Had trouble reading the following entries in the crawldb:"

        for line in trouble_list:

            print line
        
        print "Skipped %s URLs because we had trouble reading them: " % str(len(trouble_list))

if __name__ == "__main__":

    x = CrawlDBParser()
#    x.dump_crawl_db()
#    x.get_crawl_db_dump()
    for whatever in x.crawl_db_url_generator():
        print whatever

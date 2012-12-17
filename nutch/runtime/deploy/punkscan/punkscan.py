import os
import sys
cwdir = os.path.dirname(__file__)
punkscan_base = os.path.join(cwdir, ".")
sys.path.append(os.path.join(punkscan_base, "hadooper"))
sys.path.append(os.path.join(punkscan_base, "config_scripts"))
sys.path.append(os.path.join(punkscan_base, "crawl_db_parser"))
sys.path.append(os.path.join(punkscan_base, "crawler"))
import reconfig_nutch
import crawldb_parser
import hadooper
import nutch
from ConfigParser import SafeConfigParser
config_parser = SafeConfigParser()
config_parser.read(os.path.join(punkscan_base,'punkscan_configs', 'punkscan_config.cfg'))
HADOOP_HOME=config_parser.get('directories','HADOOP_HOME')
NUTCH_HOME=config_parser.get('directories','NUTCH_HOME')

def configure_punkscan():
    '''configure punkscan, get ready for the crawl'''

    config_r = reconfig_nutch.ConfigoRoboto()
    config_r.generate_template_file()
    config_r.generate_seed_list()
    config_r.clear_and_put_seed_list_on_hdfs()

def crawl():
    '''Perform the crawl against the sites'''

    nutch.NutchController().crawl()

def parse_crawl_db():
    '''Delete previous crawl db on HDFS and local fs,
    Dump the crawl db to HDFS, copy from HDFS to local
    filesystem'''

    db_parso = crawldb_parser.CrawlDBParser()
    db_parso.dump_crawl_db()
    db_parso.get_crawl_db_dump()

    return db_parso.crawl_db_url_generator()

def execute():

        configure_punkscan()
        crawl()

        for urls in parse_crawl_db():
            print urls
                        
if __name__ == "__main__":

    configure_punkscan()
    crawl()

    for urls in parse_crawl_db():
        print urls
                

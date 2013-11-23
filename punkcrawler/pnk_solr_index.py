import requests
from ConfigParser import ConfigParser
conf = ConfigParser()
conf.read("punkcrawler.cfg")

def commit():
        solr_summ_commit_url = conf.get("punkcrawler", "solr_summary_url") + "?commit=true"
        r = requests.get(solr_summ_commit_url)

if __name__ == "main":
    commit()    
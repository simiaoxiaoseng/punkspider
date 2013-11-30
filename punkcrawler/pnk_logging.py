import sys
import datetime
from ConfigParser import ConfigParser
conf = ConfigParser()
conf.read("punkcrawler.cfg")

def pnk_log(module, msg):
    i = datetime.datetime.now()
    sys.stderr.write("PunkCRAWLER %s %s: %s\n" % (i.isoformat(), module, msg))

    f = open("punkcrawler.log", "a")
    f.write("PunkCRAWLER %s %s: %s\n" % (i.isoformat(), module, msg))
    f.close()
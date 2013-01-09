import sys
import os
import subprocess
cwdir = os.path.dirname(__file__)
punkscan_base = os.path.join(cwdir, "../")
sys.path.append(os.path.join(punkscan_base, 'hadooper'))
import hadooper
from ConfigParser import SafeConfigParser
config_parser = SafeConfigParser()
config_parser.read(os.path.join(punkscan_base,'punkscan_configs', 'punkscan_config.cfg'))
HADOOP_HOME=config_parser.get('directories','HADOOP_HOME')
NUTCH_HOME=config_parser.get('directories','NUTCH_HOME')

class Hadooper:
    '''Some basic Hadoop operations.'''

    def __init__(self):

        self.hadoop_bin = os.path.join(HADOOP_HOME, 'bin', 'hadoop')
	
    def copyToLocal(self, src, dst):

        shell_call_list = [self.hadoop_bin, 'dfs', '-copyToLocal', src, dst]
        output = subprocess.Popen(shell_call_list).communicate()[0]

    def copyFromLocal(self, src, dst):

        shell_call_list = [self.hadoop_bin, 'dfs', '-copyFromLocal', src, dst]
        output = subprocess.Popen(shell_call_list).communicate()[0]

    def rmr(self, dst):

        shell_call_list = [self.hadoop_bin, 'dfs', '-rmr', dst]
        output = subprocess.Popen(shell_call_list).communicate()[0]


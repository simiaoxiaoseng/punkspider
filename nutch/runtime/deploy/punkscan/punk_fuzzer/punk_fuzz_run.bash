#!/bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd )"
#cd $DIR
#run crawl to generate urls to fuzz
#cd ..
#python punkcrawler.py
#cd $DIR

#local mode
#python punk_mapreduce.py < urls_to_fuzz > output_local

#distributed mode
python punk_mapreduce.py -r hadoop --cmdenv PYTHONPATH=$DIR\
 --file punk_fuzz.py --file fuzzer_config/fuzz_config_parser.py\
 --file fuzzer_config/punk_fuzz.cfg.xml --python-archive includes.tar.gz\
 < urls_to_fuzz > output_distributed

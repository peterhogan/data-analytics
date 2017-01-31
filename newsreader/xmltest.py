#######################################
############### Imports ############### 
#######################################
from kafka import KafkaProducer
import kafka
from pycorenlp import StanfordCoreNLP
from glob import glob
from lxml import etree
import urllib.request
from bs4 import BeautifulSoup
import os
from time import time
from time import sleep
from datetime import timedelta
import sys
import argparse
import logging
import xml.etree.ElementTree as ET
import extractionFunctions as EF
import json

############################################
############### Inital setup ############### 
############################################

# Function to read nice byte sizes:
def size_format(x, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(x) < 1024.0:
            return "%3.1f%s%s" % (x, unit, suffix)
        x /= 1024.0
    return "%.1f%s%s" % (x, 'Yi', suffix)

##############################
########## Startup ###########
##############################

# Parse command line arguments

parser = argparse.ArgumentParser(description="Read news articles from RSS feeds given by the --file option, and send them to kafka_broker kafka_topic.")
parser.add_argument("-f", "--file", help="path of RSS sources file",
                    action="store", required=True)
parser.add_argument("-q", "--quiet", help="output on error only",
                    action="store_true", required=False)
parser.add_argument("-v", "--verbose", help="log level debug",
                    action="store_true", required=False)
parser.add_argument("-o", "--output", help="output the entity extracted feeds to a JSON file",
                    action="store", required=False)
parser.add_argument("-s", "--server",
                    help="URL of the Stanford CoreNLP server (default: http://localhost:9000)",
                    action="store", required=True, default="http://localhost:9000")
arg = parser.parse_args()

# Logging
if arg.quiet:
    logging.basicConfig(level=logging.ERROR)
elif arg.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
log = logging.getLogger(name='newsreaderLog')

# open the port to the NLP server
nlp = StanfordCoreNLP(arg.server)

# start timer
start = time()
log.debug("Starting timer")

# Janes namespace Dict
ns = {'janes': 'http://dtd.janes.com/2002/Content/',
      'xlink': 'http://www.w3.org/1999/xlink',
      'dc': 'http://purl.org/dc/elements/1.1/',
      'jm': 'http://dtd.janes.com/2005/metadata/'}

with open(arg.output, "+w") as outputfile:
        # pull out the news sources one by one
    for filename in glob(os.path.join(arg.file, "*.xml")):

        # open the file
        with open(filename, "r", encoding="ISO-8859-1") as xmlfile:
            try:
                tree = ET.parse(filename)
                root = tree.getroot()
            except etree.XMLSyntaxError:
                logging.error("failed at xml parse")
                continue

            title = root.findall('janes:title',ns)[0].text

            paras = []
            for section in root.findall('janes:sect1', ns):
                for paragraph in section.findall('janes:para', ns):
                    paras.append(paragraph.text)
            
            message = title+" || "+paras[0]
            message_content = title+" "+paras[0]

            outputfile.write(json.dumps(EF.encodeNER(message,EF.extractNER(message_content,nlp)), sort_keys=True))

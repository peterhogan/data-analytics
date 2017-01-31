#######################################
############### Imports ############### 
#######################################
from kafka import KafkaProducer
import kafka
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
parser.add_argument("kafka_broker", help="URL of the kafka broker in the form URL:PORT")
parser.add_argument("kafka_topic", help="kafka topic name to send to")
parser.add_argument("-v", "--verbose", help="log level DEBUG",
                    action="store_true", default=False)
parser.add_argument("-q", "--quiet", help="only output on error",
                    action="store_true", default=False)
parser.add_argument("-l", "--live", help="print the article name on send",
                    action="store_true", default=False)
parser.add_argument("-r", "--running", help="output a running total of files sent",
                    action="store_true", default=False)
parser.add_argument("-i", "--interactive", help="wait for keypress to start sending articles",
                    action="store_true", default=False)
parser.add_argument("-w", "--wait", help="how many seconds to pause before iterating over the source list (only when running in continuous mode)", action="store", type=int, default=60)
parser.add_argument("-f", "--file", help="path of RSS sources file",
                    action="store", required=True)
parser.add_argument("-D", "--database", help="path of the DB used to store the article data",
                    action="store", required=False, default="globalGUID.log")
parser.add_argument("-O", "--output", help="list the outputs to send",
                    choices=["all","title","description","date","GUID","roottitle","rootdate"], default="all")
parser.add_argument("-c", "--continuous", help="keep iterating over the RSS file list sources - Ctrl-C to quit",
                    action="store_true", default=False)
parser.add_argument("-n", "--number-of-messages", help="give the number of messages to send, 0 = all", action="store", type=int, default=0)
args = parser.parse_args()

# Logging
if args.quiet:
    logging.basicConfig(level=logging.ERROR)
elif args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
log = logging.getLogger(name='newsreaderLog')

# specify the location of the global GUID file
globalGUID = args.guid
log.debug('location of guid file: %s',globalGUID)

# check before streaming
if args.interactive:
    cont = input("Start streaming %s? (y/n) " % rssfeedfile)
    if cont == 'y':
        pass
    else:
        quit('Now exiting, no files downloaded')

# start timer
start = time()
log.debug("Starting timer")

###################################################
######### Define the ancilliary functions ######### 
###################################################


# function to read the root titles from an already-parsed rss xml file
def RootTitles(read_file):
    try:
        titleout = read_file.xpath('//channel/title')[0].text
    except IndexError:
        titleout = ' '
        # would like some sort of regex title on the filename: titleout = re.search('^[a-zA-Z]+',FILENAME).group(0)
        # but how to get filename?
    return titleout

# function to read the build date from an already-parsed rss xml file - if it exists
def BuildDates(read_file):
    try:
        buildout = read_file.xpath('//channel/lastBuildDate')[0].text
    except IndexError:
        buildout = ' ' 
    return buildout

###################################
######### Start Streaming ######### 
###################################

# print out values before streaming:
if args.quiet == False:
    print("Reading from:\t\t",args.file)
    print("GUID file:\t\t", args.guid)
    print("Kafka broker:\t\t", args.kafka_broker)
    print("Kakfa topic:\t\t", args.kafka_topic)

# define the keep running variable:
keep_running = True

# define the EarlyExit class:
class EarlyExit(Exception):
        pass

# define the counter variables:
filesread = 0
articlessent = 0
duplicates = 0

# start the kafka producer
log.debug("starting Kafka communication: %s", args.kafka_broker)
try:
    producer = KafkaProducer(bootstrap_servers=args.kafka_broker)
except kafka.errors.NoBrokersAvailable:
    log.error("No brokers found running")
    log.info("Ensure Zookeeper and Kakfa are running and retry")
    quit()

try:
    while keep_running:
        # pull out the news sources one by one
        for filename in glob(os.path.join(args.file, "*.xml")):
            # open and save the global guid file into guid_list (slow - alternative?)
            with open(globalGUID, 'r') as masterGUID:
                guid_list = masterGUID.read().splitlines()

            # increment the files read counter
            filesread += 1

            # open the file
            with open(filename) as xmlfile:
                try:
                    xml = etree.parse(xmlfile)
                except etree.XMLSyntaxError:
                    continue

                # Get the item title
                try:
                    itemtitle = xml.xpath('//janes:record/janes:title').text.encode('utf-8')
                except (TypeError,IndexError,AttributeError):
                    itemtitle = 'NO ITEM TITLE FOUND'

                log.debug("Item title: %s",itemtitle)
                print(itemtitle)
                '''

                # Get GUID 
                try:
                    itemguid = rssfile.xpath('//channel/item/guid')[i].text
                except IndexError:
                    itemguid = rssfile.xpath('//channel/item/title')[i].text

                # pass iteration if it already exists in log file
                if itemtitle in guid_list or itemguid in guid_list:
                    if itemtitle in guid_list:
                        log.debug("%s in guid log file", itemtitle)
                    if itemguid in guid_list:
                        log.debug("%s in guid log file", itemguid)
                    # increment the duplicates counter then skip
                    duplicates += 1
                    log.debug("Number of duplicates: %i", duplicates)
                    continue
                else:
                    log.debug("Unique article: %s", itemtitle)
                    with open(globalGUID, 'a+') as masterGUIDw:
                        log.debug("Global guid file opened")
                        masterGUIDw.write(str(itemguid)+'\n'+str(itemtitle)+'\n')
                        log.debug("Global guid file writen to")
                    log.debug("Global guid file closed")
                # decode the item title
                try:
                    itemtitle = itemtitle.decode('utf-8')
                except AttributeError:
                    continue

                # Get the item Description and remove any html tags
                try:
                    itemdescpre = rssfile.xpath('//channel/item/description')[i].text
                    itemdescsoup = BeautifulSoup(itemdescpre, "lxml")
                    itemdesc = itemdescsoup.get_text()
                except (TypeError, IndexError):
                    itemdesc = ' ' 

                # Get Publish Dates
                try:
                    itempubdate = rssfile.xpath('//channel/item/pubDate')[i].text
                except IndexError:
                    itempubdate = ' ' 

                if args.output == "all":
                    log.debug("Outputting all fields")
                    rss_article_tuple = (itemtitle,itemdesc,itempubdate,itemguid,itemroottitle,itemrootdate)
                    log.debug("Article tuple created: %r", rss_article_tuple)
                    try:
                        rss_article = ' || '.join(rss_article_tuple)
                        log.debug("Article: %r", rss_article)
                    except TypeError:
                        log.error("Type error creating article")
                        pass
                elif args.output == "title":
                    rss_article = itemtitle
                elif args.output == "description":
                    rss_article= itemdesc
                elif args.output == "date":
                    rss_article= itempubdate
                elif args.output == "GUID":
                    rss_article= itemguid
                elif args.output == "roottitle":
                    rss_article= itemroottitle
                elif args.output == "rootdate":
                    rss_article= itemrootdate


                try:
                    producer.send(args.kafka_topic, rss_article.encode('utf-8'))
                    articlessent += 1
                except NameError:
                    continue
                
                if args.number_of_messages > 0:
                    if args.number_of_messages <= articlessent:
                        raise EarlyExit

                if args.quiet == False and args.live == False and args.running:
                    print("Articles sent:\t\t", articlessent, end='\r', flush=True)

                if args.quiet == False and args.live:
                    try:
                        print("Source:",itemroottitle,"Article:",itemtitle)
                    except UnicodeEncodeError:
                        continue

                else:
                    continue
                    '''

            # for option -c, --continuous
        if args.continuous:
            sleep(args.wait)
        else:
            keep_running = False
except EarlyExit:
    pass

totaltime = time() - start
if args.quiet == False or args.running == False:
    print('\nFiles read:\t\t', filesread)
    print('Articles sent:\t\t', articlessent)
    print('Duplicate articles:\t', duplicates)
    print('Time taken:\t\t',str(timedelta(seconds=totaltime)))
    print('Size of GUID file:\t', globalGUID,"-", size_format(int(os.stat(globalGUID).st_size)))

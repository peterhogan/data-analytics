#######################################
############### Imports ############### 
#######################################
from kafka import KafkaProducer
import kafka
from lxml import etree
import urllib.request
import re
import os, errno
from time import time
from datetime import timedelta
import sys

from kfk_rss_read import *

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

# specify the location of the feed file (text file full of rss links)
rssfeedfile = 'rssfeeds.txt'

# specify the location of the global GUID file
globalGUID = 'globalGUID.log'

# check before streaming
#cont = input("Start streaming %s? (y/n) " % rssfeedfile)
#if cont == 'y':
#    pass
#else:
#    quit('Now exiting, no files downloaded')

# start timer
start = time()

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

# start the kafka producer
try:
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
except kafka.errors.NoBrokersAvailable:
    print("##### No brokers found running #####")
    print("Ensure Zookeeper and Kakfa are running and retry")
    quit()

# Open the rssfeeds text file for parsing
with open(rssfeedfile) as feedsources:
    rssfeeds = feedsources.read().splitlines()

# define the counter variables:
filesread = 0
articlessent = 0
duplicates = 0
#timestreaming = 0
#kafkainstance = 
#totaldownload = 0

# pull out the news sources one by one
for feed in rssfeeds:
    if feed.startswith('http'):
        # open and save the global guid file into guid_list (slow - alternative?)
        with open(globalGUID, 'r') as masterGUID:
            guid_list = masterGUID.read().splitlines()

        # increment the files read counter
        filesread += 1

        # download the file by url
        try:
            response = urllib.request.urlopen(feed)
        except RemoteDisconnected:
            continue
        try:
            rssfile = etree.parse(response)
        except etree.XMLSyntaxError:
            continue

        # get root title with RootTitle function
        itemroottitle = RootTitles(rssfile)

        # get build date with BuildDates function (if possible)
        itemrootdate = BuildDates(rssfile)

        for i in range(len(rssfile.xpath('//channel/item'))):

            # Get GUID and pass iteration if it already exists
            try:
                itemguid = rssfile.xpath('//channel/item/guid')[i].text
            except IndexError:
                itemguid = rssfile.xpath('//channel/item/title')[i].text

            if itemguid in guid_list:
                # increment the duplicates counter then skip
                duplicates += 1
                continue
            else:
                with open(globalGUID, 'a+') as masterGUIDw:
                    masterGUIDw.write(str(itemguid)+'\n')

            # Get the item title
            try:
                itemtitle = rssfile.xpath('//channel/item/title')[i].text
            except IndexError:
                itemtitle = 'NO ITEM TITLE FOUND'

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

            rss_article_tuple = (itemtitle,itemdesc,itempubdate,itemguid,itemroottitle,itemrootdate)
            rss_article = ' | '.join(rss_article_tuple)

            producer.send('python-test', rss_article.encode('utf-8'))


            articlessent += 1

            try:
                print("Source:",itemroottitle,"Article:",itemtitle)
            except UnicodeEncodeError:
                continue

    # Flatten GUID file to prevent duplicates being missed through nested lists
    #guidlist = list(chain(*guidlist))

    else:
        continue
totaltime = time() - start
print('\nFiles read:', filesread)
print('Articles sent:', articlessent)
print('Duplicate articles:', duplicates)
print('Time taken:',str(timedelta(seconds=totaltime)))
print('Size of globalGUID.log:', size_format(int(os.stat(globalGUID).st_size)))

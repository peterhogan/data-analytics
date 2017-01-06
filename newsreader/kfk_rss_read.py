#######################################
############### Imports ############### 
#######################################
from lxml import etree
from bs4 import BeautifulSoup
from itertools import chain
import os
import re

############################################
############### Inital setup ############### 
############################################

# specify the directory to pull feeds from (default from get_rss_feeds.py)
root_dir = 'newsfeeds/'

# Define unique function
def unique(items):
    seen = set()
    for i in range(len(items)-1, -1, -1):
        it = items[i]
        if it in seen:
            del items[i]
        else:
            seen.add(it)

####################################################
############### Defining the outputs ############### 
####################################################

# Function to collect all the sources picked up in root_dir
def rss_sources(root_directory):
    return [ rssfile for rssfile in os.listdir(root_directory) ]

# print all sources
def rss_sources_print(root_directory):
    sources = rss_sources(root_directory)
    for j in set([re.search('^[a-zA-Z]+',i).group(0) for i in sources]):
        print(j)
    return 

# function to read the root titles from an already-parsed rss xml file
def roottitles(read_file):
    try:
        titleout = read_file.xpath('//channel/title')[0].text
    except IndexError:
        titleout = re.search('^[a-zA-Z]+',rssfile).group(0)
    return titleout

# function to read the build date from an already-parsed rss xml file - if it exists
def builddates(read_file):
    try:
        buildout = read_file.xpath('//channel/lastBuildDate')[0].text
    except IndexError:
        buildout = ' '
    return buildout

# Pull all item detail from an rss xml file
def itemdetail(read_file, verbose = True, getguid = False, localGuid = True, masterGUIDFile = ''):

    # Create an article list
    rss_articles = []

    # read from the master GUID file or create a local GUID list (default) to prevent duplicate articles
    if localGuid == True:
        guidlist = []
    else:
        guidlist = masterGUIDFile

    for i in range(len(read_file.xpath('//channel/item'))):
        # Get GUID and pass iteration if it already exists
        try:
            itemguid = read_file.xpath('//channel/item/guid')[i].text
        except IndexError:
            itemguid = read_file.xpath('//channel/item/title')[i].text
        if itemguid in guidlist:
            continue
        else:
            guidlist.append(itemguid)

        # Get the item title
        try:
            itemtitle = read_file.xpath('//channel/item/title')[i].text
        except IndexError:
            itemtitle = 'NO ITEM TITLE FOUND'

        # Get the item Description and remove any html tags
        try:
            itemdescpre = read_file.xpath('//channel/item/description')[i].text
            itemdescsoup = BeautifulSoup(itemdescpre, "lxml")
            itemdesc = itemdescsoup.get_text()
        except IndexError:
            itemdesc = ' '

        # Get Publish Dates
        try:
            itempubdate = read_file.xpath('//channel/item/pubDate')[i].text
        except IndexError:
            itempubdate = ' '

        # Add all the tags to the article list
        #if getguid == True:
        #    rss_articles.append(itemguid)
        if verbose == True:
            itemroottitle = roottitles(read_file)
            itemrootdate = builddates(read_file)
            rss_articles.append([itemtitle,itemdesc,itempubdate,itemguid,itemroottitle,itemrootdate])
        else:
            rss_articles.append([itemtitle,itemdesc])

    # Flatten GUID file to prevent duplicates being missed through nesting lists
    guidlist = list(chain(*guidlist))

    if getguid == True:
        return guidlist
    return rss_articles

# Read an XML file
def ReadXML(root_directory,xmlfile):
    return etree.parse(root_directory + xmlfile)

# Create GUID list
def GuidList(root_directory):
    masterguidlist = []
    for i in range(len(rss_sources(root_directory))):
        rssxmlfile = rss_sources(root_directory)[i]
        inguidfile = ReadXML(root_dir,rssxmlfile)
        masterguidlist.append(itemdetail(inguidfile, getguid = True))
    return list(chain(*masterguidlist))

# Read all XML files in root_dir
def AllItemDetail(root_directory):
    return [itemdetail(ReadXML(root_directory,i)) for i in  rss_sources(root_directory)]


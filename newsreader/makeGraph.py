from time import sleep
from time import time
import argparse
import json
import logging
from collections import Counter

timestart = time()

##### COMMAND LINE ARGUMENTS #####
parser = argparse.ArgumentParser(description="Determine relationships between data in JSON format")
parser.add_argument("inputfile", help="input file to read nodes from")
parser.add_argument("-q", "--quiet", help="only output on error",action="store_true")
parser.add_argument("-v", "--verbose", help="log level DEBUG",action="store_true")
parser.add_argument("-s", "--server", help="server address for geo queries",
        action="store", required=False, default="http://localhost:9090")
parser.add_argument("-o", "--output", help="output the relationships to a JSON file",
                                    action="store", required=False)

args = parser.parse_args()

##### LOGGING #####
if args.quiet:
    logging.basicConfig(level=logging.ERROR)
elif args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
log = logging.getLogger('relaLog')


##### Functions #####

# List all unique entities
def listUniqueEntities(data,matchlist):
    # list of sublists of unique entities
    uniqueEntities = []

    # iterate over all entities to match (fn input)
    for match in matchlist:
        log.debug("Now scanning for: %s",match)

        # form the container list for this entity type
        matchlistname = str(match)+"entities"
        log.debug("The match list name is: %r", matchlistname)
        matchlistname = []

        # iterate over each entry in the input data
        for entry in data:
            try:
                for matchtype in entry[match]:
                    log.debug("Now matching against: %s",matchtype)
                    matchedPair = (entry[match][matchtype],match[0:-1]) 
                    log.debug("Matched pair: %r",matchedPair)
                    if matchedPair not in matchlistname:
                        matchlistname.append(matchedPair)
                        log.debug("Current matches: %r", len(matchlistname))
            except KeyError:
                pass
        uniqueEntities.append(sorted(matchlistname))
        log.debug("Finished with matchtype %s",match)

    return uniqueEntities

# define function to make unique entities into JSON format (and output?)
def entityNodes(data):
    return

# define read function
def readEntities(article, matchlist):
    entityList = []
    for entity in match_list:
        try:
            entityList.append(article[entity])
        except KeyError:
            pass
    return entityList

# define edge creation function
def makeEdges(data,matchlist):

    # extract the nodes:
    entity_nodes = listUniqueEntities(data,matchlist)

    # produce flat list
    entity_nodes_name = []
    for entry in entity_nodes:
        for i in entry:
            entity_nodes_name.append(i[0])

    # init edge list
    edges = []

    # iterate over all articles in the data
    for article in data:

        # extract entities per article
        for entity in readEntities(article, matchlist):

            # look at value for matching
            for key,value in entity.items():

                # if it matches append it to the edges list as a pair
                if value in entity_nodes_name:
                    edges.append((('source',article['title']),('target',value)))

    return dict(edges)

# list of entites to match
match_list = ["PERSONS","LOCATIONS","ORGANIZATIONS","DATES","MISCS"]

log.info("Opening: %s", args.inputfile)
with open(args.inputfile, 'r') as f:
    nodedata = json.load(f)

#print(listUniqueEntities(nodedata,match_list)[0])
data1 = listUniqueEntities(nodedata,match_list)
lengths = [len(data1[i]) for i in range(len(data1))]

uniqueEntityList = []
for i in listUniqueEntities(nodedata,match_list):
    #print(i)
    for j in i:
        uniqueEntityList.append(j[0])

#print(uniqueEntityList)
mentions = []
for article in nodedata:
    for entity in readEntities(article, match_list):
        for key,value in entity.items():
            if value in uniqueEntityList:
                mentions.append(value)

def makeArticleNodes(data, matchlist):
    # init article list
    article_list = []    

    # iterate over articles
    for article in data:
        article_list.append({"id" : article['title'],
                             "group" : 1})

    return article_list

def makeLinks(data,matchlist):
    link_list = []
    for article in data:
        for entity in readEntities(article, matchlist):
            for key,value in entity.items():
                link_list.append({"source": article['title'],
                                  "target": value})
    return link_list

def makeEntityNodes(data,matchlist):
    identifier = 2
    entity_list = []

    for entitytype in listUniqueEntities(data,matchlist):
        for etype in entitytype:
            entity_list.append({"id": etype[0], "group": identifier})
        identifier += 1

    return entity_list

def knitGraph(data,matchlist):
    return {"nodes": makeArticleNodes(data,matchlist)+makeEntityNodes(data,matchlist), "links": makeLinks(data,matchlist)}

#makeEntityNodes(nodedata, match_list)
#print(makeEntityNodes(nodedata, match_list))
print(json.dumps(knitGraph(nodedata,match_list), sort_keys=True))

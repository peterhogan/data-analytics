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

# list of entites to match
match_list = ["PERSONS","LOCATIONS","ORGANIZATIONS","DATES","MISCS"]

log.info("Opening: %s", args.inputfile)
with open(args.inputfile, 'r') as f:
    nodedata = json.load(f)

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

#print(listUniqueEntities(nodedata,match_list)[0])
data1 = listUniqueEntities(nodedata,match_list)
lengths = [len(data1[i]) for i in range(len(data1))]
#print(lengths)
#for x,y in zip(match_list,lengths):
    #print(x,y)

# Function to check if article contain entities
def checkMatches(article, entities):
    return
    

def matchNodes(nodedata, matchlist):
    totalmatches = []
    titlelist= []
    duplicates = 0

    for left in nodedata:
        leftmatches = 0
        titlelist.append(left['title'])
        for right in nodedata:
            if left["guid"] != right["guid"]:
                if right['title'] not in titlelist:
                    for entity in matchlist:
                        try:
                            for x in left[entity]:  
                                for y in right[entity]:
                                    if left[entity][x] == right[entity][y]:
                                        leftmatches += 1
                                    else:
                                        pass
                        except KeyError:
                            pass
                else:
                    duplicates += 1
                    pass
            else:
                pass
        if leftmatches > 0:
            totalmatches.append((leftmatches,left['title']))
    return totalmatches

# define read function
def readEntities(article, matchlist):
    entityList = []
    for entity in match_list:
        try:
            entityList.append(article[entity])
        except KeyError:
            pass
    return entityList



uniqueEntityList = []
for i in data1:
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

#print(mentions)
print(Counter(mentions).most_common(10))

quit()

##### TO DO #####
# 1) match entities in the articles
# 2) print JSON nodes for the unique entities
# 3) print JSON edges for relationship

'''
for article in articlelist:
    for entity in allEntities:
        if entity in article
'''


tmatch = matchNodes(nodedata, match_list)
data1 = sorted(tmatch,reverse=True)[0:10]
for item in data1:
    print(item)


finish = time() - timestart

matches = sum([i for i in map(lambda x: x[0],tmatch)])

#print('Duplicates:',duplicates)
print("highest degree", max(tmatch))
print("total matches",matches)
print("time taken", finish)
print(len(nodedata),"articles")

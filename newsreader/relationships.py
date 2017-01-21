from time import sleep
from time import time
import argparse
import json
import logging

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


##### INITIALISATION #####

# list of entites to match
match_list = ["PERSONS","LOCATIONS","ORGANIZATIONS","DATES","MISCS"]


log.info("Opening: %s", args.inputfile)
with open(args.inputfile, 'r') as f:
    nodedata = json.load(f)

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
'''

finish = time() - timestart
for top in sorted(totalmatches,reverse=True)[0:10]:
    print(top)

matches = sum([i for i in map(lambda x: x[0],totalmatches)])

print('Duplicates:',duplicates)
print("highest degree", max(totalmatches))
print("total matches",matches)
print("time taken", finish)
print(len(nodedata),"articles")
'''

from time import sleep
from time import time
import argparse
import json
import logging
from collections import Counter

##### COMMAND LINE ARGUMENTS #####
parser = argparse.ArgumentParser(description="Determine relationships between data in JSON format")
parser.add_argument("inputfile", help="input file to read nodes from")
parser.add_argument("query", help="query text")
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

## START ##
start_time = time()

##### Functions #####

def nodeLinks(graphdata, query):
    node_links = []
    for link in graphdata['links']:
        node_pair = (link['target'],link['source'])
        if node_pair[0] == query and node_pair not in node_links:
            node_links.append(node_pair)
    return node_links

def allTargets(graphdata):
    all_targets = []
    for link in graphdata['links']:
        if link['target'] not in all_targets:
            all_targets.append(link['target'])
    return all_targets

def nodeCount(graphdata):
    return len(graphdata['nodes'])

def linkCount(graphdata):
    return len(graphdata['links'])

def nodeDegree(graphdata,node):
    return len(nodeLinks(graphdata,node))

def allNodeDegrees(graphdata):
    all_targets = allTargets(graphdata)
    node_degrees = []
    for i in sorted(all_targets):
        node_degrees.append((nodeDegree(graphdata,i),i))
    return node_degrees

def nDegreeNodes(graphdata, n):
    all_targets = allTargets(graphdata)
    node_degrees = []
    for i in sorted(all_targets):
        if nodeDegree(graphdata,i) > n:
            node_degrees.append(nodeDegree(graphdata,i),i)
    return node_degrees

def pageRankC(graphdata, node):
    c = 0
    for edge in graphdata['links']:
        if edge['source'] == node:
            c += 1
    return c


def pageRankL(graphdata,source,target):
    all_links = allTargets(graphdata)
    if (source,target) in all_links:
        return 1
    return 0

def nodePageRank(node,graphdata):
    noderanklist = []
    iterations = 0
    for othernode in graphdata['nodes']:
        print('now on',othernode['id'],"with pagerankC:",pageRankC(graphdata,othernode['id']))
        if othernode['id'] == graphdata['nodes'][0]['id']:
            return 0.15
        elif pageRankC(graphdata,othernode['id']) != 0:
            iterations += 1
            noderanklist.append((pageRankL(graphdata,node,othernode['id'])/pageRankC(graphdata,othernode['id']))*nodePageRank(othernode['id'],graphdata))
        else:
            pass
        if iterations > 0:
            print(iterations)
    return (1-0.85)*(0.85*sum(noderanklist))

log.info("Opening: %s", args.inputfile)
with open(args.inputfile, 'r') as f:
    graphinput = json.load(f)

print("nodeCount:",nodeCount(graphinput))
print("linkCount:",linkCount(graphinput))
rankCs = []
for node in graphinput['nodes']:
    if pageRankC(graphinput,node['id']) > 10:
        rankCs.append((node['id'],pageRankC(graphinput,node['id'])))

def factorial(n):
    if n == 0:
        return 1
    return n*factorial(n-1)

total_nodes = nodeCount(graphinput)**2 

iteration = 0
for source in graphinput['nodes']:
    for target in graphinput['nodes']:
        cscore = pageRankC(graphinput,target['id'])
        lscore = pageRankL(graphinput,source['id'],target['id'])
        if lscore > 0:
            print("source:",source['id'],"target:",target['id'],"lscore:",lscore,"cscore:",cscore)
        iteration += 1
        print((iteration/total_nodes)*100,"%",end='\r')

## FINISH ##
runtime = time() - start_time
print("Run time:",runtime)

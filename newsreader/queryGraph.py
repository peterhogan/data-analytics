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


##### Functions #####

log.info("Opening: %s", args.inputfile)
with open(args.inputfile, 'r') as f:
    graphinput = json.load(f)

def nodeLinks(graphdata, query):
    node_links = []
    for link in graphdata['links']:
        if link['target'] == query:
            node_links.append(((link['target'],link['source'])))
    return node_links

all_targets = []
for link in graphinput['links']:
    if link['target'] not in all_targets:
        all_targets.append(link['target'])

node_degrees = []
for i in sorted(all_targets):
    node_degrees.append((len(nodeLinks(graphinput,i)),i))

high_node_degrees = []
for i in sorted(all_targets):
    if len(nodeLinks(graphinput,i)) > 2:
        high_node_degrees.append((len(nodeLinks(graphinput,i)),i))

print(sorted(high_node_degrees, reverse=True))


quit("Finish")

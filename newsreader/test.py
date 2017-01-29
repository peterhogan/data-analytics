from time import sleep
import os
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
parser.add_argument("-e","--edges", help="output the edges only", action="store_true")
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

def tail(f, n, offset=0):
    stdin,stdout = os.popen2("tail -n "+n+offset+" "+f)
    stdin.close()
    lines = stdout.readlines(); stdout.close()
    return lines[:,-offset]

with open(args.inputfile, '+r') as f:
    print(tail(f,1))

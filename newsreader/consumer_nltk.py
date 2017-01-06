#######################################
############### Imports ############### 
#######################################
from kafka import KafkaProducer
from kafka import KafkaConsumer
#import re
#import os, errno
from time import time
from datetime import timedelta
from atexit import register
import sys

from kfk_rss_read import *

############################################
############### Inital setup ############### 
############################################
## Function to read nice byte sizes:
#def size_format(x, suffix='B'):
#    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
#        if abs(x) < 1024.0:
#            return "%3.1f%s%s" % (x, unit, suffix)
#        x /= 1024.0
#    return "%.1f%s%s" % (x, 'Yi', suffix)
#
## specify the location of the feed file (text file full of rss links)
#rssfeedfile = 'rssfeeds.txt'
#
## specify the location of the global GUID file
#globalGUID = 'globalGUID.log'
#
## check before streaming
#cont = input("Start streaming %s? (y/n) " % rssfeedfile)
#if cont == 'y':
#    pass
#else:
#    quit('Now exiting, no files downloaded')

def Ending(kafka_consumer):
    kafka_consumer.close()
    print('Time taken:', str(timedelta(seconds=time()-start)))
    print('Messages received:', filesread)

# start timer
start = time()

###################################
######### Start Receiving ######### 
###################################

# define masterlog
masterlog ='masterlog.txt'

# define the counter variables:
filesread = 0

# create a list for all articles
all_articles = []

# start the kafka consumer
#consumer = KafkaConsumer('python-test',
#                         fetch_min_bytes=300000,
#                         fetch_max_wait=300000,
#                         auto_commit_interval_ms=1000,
#                         max_poll_records=10,
#                         bootstrap_servers=['localhost:9092'])

consumer = KafkaConsumer('python-test',
                         bootstrap_servers=['localhost:9092'])

register(Ending,consumer)

# read messages
#with open(masterlog, 'a+') as master:
#    for msg in consumer:
#        if filesread < 10:
#            filesread += 1
#            master.write(msg.value.decode('utf-8')+'\n')
#        else: break

with open(masterlog, 'a+') as master:
    for msg in consumer:
        filesread += 1
        master.write(msg.value.decode('utf-8')+'\n')

print(all_articles)

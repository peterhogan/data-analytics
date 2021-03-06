#######################################
############### Imports ############### 
#######################################
from kafka import KafkaProducer
from kafka import KafkaConsumer
from time import time
from datetime import timedelta
from atexit import register
from pycorenlp import StanfordCoreNLP
import extractionFunctions as EF
import argparse
import json

############################################
############### Inital setup ############### 
############################################

# Parse command line arguments

parser = argparse.ArgumentParser(description="Read news articles from kafka topics and extract entities from text.")
parser.add_argument("kafka_broker", help="URL of the kafka broker in the form URL:PORT")
parser.add_argument("kafka_topic", help="kafka topic name to listen to")
parser.add_argument("-q", "--quiet", help="only output on error",action="store_true")
parser.add_argument("-s", "--server", 
                    help="URL of the Stanford CoreNLP server (default: http://localhost:9000)",
                    action="store", required=True, default="http://localhost:9000")
parser.add_argument("-b", "--from-beginning", help="read from the beginning of the topic",
                            action="store_true", default=False)
parser.add_argument("-o", "--output", help="output the entity extracted feeds to a JSON file",
                            action="store", required=False)

args = parser.parse_args()

## define the 'ending' function
def Ending(kafka_consumer,jlist):
    if args.output:
        json.dump(jlist, outputfile, sort_keys=True, ensure_ascii=True)
        outputfile.close()
    kafka_consumer.close()
    print('Time taken:', str(timedelta(seconds=time()-start)))
    print('Messages received:', filesread)

# start timer
start = time()

###################################
######### Start Receiving ######### 
###################################

# define the counter variables:
filesread = 0

# start the kafka consumer
consumer = KafkaConsumer(args.kafka_topic, bootstrap_servers=[args.kafka_broker])

# initialise the JSON list for formatting
jsonList = []

# register the exit code
register(Ending,consumer,jsonList)

# open the port to the NLP server
nlp = StanfordCoreNLP(args.server)

# show listening (if not quiet)
if not args.quiet:
    print("Now listening on",args.kafka_broker,args.kafka_topic,"with NER on",args.server+"... ")

# read messages
if args.output:
    outputfile = open(args.output, '+w')
    try:
        for msg in consumer:
            filesread += 1
            message = msg.value.decode('utf-8')
            message_content = ' '.join(message.split(" || ")[0:2])
            jsonList.append(EF.encodeNER(message,EF.extractNER(message_content,nlp)))
            if not args.quiet:
                print("Files read:",filesread, end='\r')
    except KeyboardInterrupt:
        pass
else:
    try:
        for msg in consumer:
            filesread += 1
            message = msg.value.decode('utf-8')
            message_content = ' '.join(message.split(" || ")[0:2])
            print(json.dumps(EF.encodeNER(message,EF.extractNER(message_content,nlp)), sort_keys=True))
    except KeyboardInterrupt:
        pass

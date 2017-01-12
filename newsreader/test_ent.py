#######################################
############### Imports ############### 
#######################################
from kafka import KafkaProducer
from kafka import KafkaConsumer
from time import time
from datetime import timedelta
from atexit import register
from pycorenlp import StanfordCoreNLP
import argparse
from collections import Counter

############################################
############### Inital setup ############### 
############################################

# Parse command line arguments

parser = argparse.ArgumentParser(description="Read news articles from kafka topics and extract entities from text.")
parser.add_argument("kafka_broker", help="URL of the kafka broker in the form URL:PORT")
parser.add_argument("kafka_topic", help="kafka topic name to listen to")
parser.add_argument("-s", "--server", 
                    help="URL of the Stanford CoreNLP server (default: http://localhost:9000)",
                    action="store", required=True, default="http://localhost:9000")
parser.add_argument("-b", "--from-beginning", help="read from the beginning of the topic",
                            action="store_true", default=False)
parser.add_argument("-n", "--topn", help="show top n items",
                            action="store", type=int, default=10)
args = parser.parse_args()

## get topN
topN = args.topn

## define the 'ending' function
def Ending(kafka_consumer):
    kafka_consumer.close()
    print('Time taken:', str(timedelta(seconds=time()-start)))
    print('Messages received:', filesread)
    print("###############################")
    print('People:',Counter(people).most_common(topN))
    print("###############################")
    print('Places:',Counter(places).most_common(topN))
    print("###############################")
    print('Organisations:',Counter(orgs).most_common(topN))
    print("###############################")
    print('Misc:',Counter(misc).most_common(topN))

## define the sorting fucntion for NEs
def appendToList(text, ner):
    if ner == "PERSON":
        people.append(text)
    elif ner == "LOCATION":
        places.append(text)
    elif ner == "ORGANIZATION": 
        orgs.append(text)
    elif ner == "MISC":
        misc.append(text)

# start timer
start = time()

# List Topics to pull out
tokenlist = ["PERSON","LOCATION","MISC","ORGANIZATION"]

# initalise buckets:
people = []
places = []
orgs = []
misc = []

###################################
######### Start Receiving ######### 
###################################

# define the counter variables:
filesread = 0

# start the kafka consumer
consumer = KafkaConsumer(args.kafka_topic,
                         bootstrap_servers=[args.kafka_broker])

# register the exit code
register(Ending,consumer)

# open the port to the NLP server
nlp = StanfordCoreNLP(args.server)

# read messages
for msg in consumer:
    # increment the file counter 
    filesread += 1
    # decode to UTF-8
    msg_decode = msg.value.decode('utf-8')
    # pull out entities
    annotate_article = nlp.annotate(msg_decode, properties={'annotators': 'ner', 'outputFormat': 'json'})
    for j in range(len(annotate_article['sentences'])):
        # reset the chamber per sentence
        chamber = []
        # iterate over tokens
        for k in range(len(annotate_article['sentences'][j]['tokens'])):

        token = annotate_article['sentences'][j]['tokens'][k]
        token_ner = token['ner']
        token_text = token['originalText']

        if token_ner in [chamber[i][1] for i in range(len(chamber))]:
            print(token_ner,'is in',[chamber[i][1] for i in range(len(chamber))])
            chamber.append((token_text,token_ner))
        else:   
            print(token_ner,'is NOT in',[chamber[i][1] for i in range(len(chamber))])
            if len(chamber) > 0:
            print('Chamber is nonempty:', chamber)
            addToList(' '.join([chamber[a][0] for a in range(len(chamber))]), chamber[0][1])
            chamber = []
            else:   
                if token_ner in tokenlist1:
                print((token_text,token_ner),'is in',tokenlist1)
                chamber.append((token_text,token_ner))
                else:   
                print(token_text,'is not an entity')
                pass

'''
        for token in annotate_article['sentences'][j]['tokens']:
            token_ner = token['ner']
            if token_ner in tokenlist:
                token_text = token['originalText']
                appendToList(token_text, token_ner)
                '''

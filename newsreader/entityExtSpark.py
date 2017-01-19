from pyspark import SparkContext
from pyspark import RDD
from pyspark import SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import *
import argparse
from pycorenlp import StanfordCoreNLP
#from nltk import word_tokenize, Text, collocations

######### CLI arguments #########
parser = argparse.ArgumentParser()
parser.add_argument("broker")
parser.add_argument("topic")
parser.add_argument("checkpoint")
parser.add_argument("-s", "--server", 
                    help="URL of the Stanford CoreNLP server (default: http://localhost:9000)",
                    action="store", required=True, default="http://localhost:9000")

args = parser.parse_args()

######### define functions ########

## counting function
def updateFunction(newValues, runningCount):
    if runningCount is None:
        runningCount = 0
    return sum(newValues, runningCount)

def functionToCreateContext():
    scc = StreamingContext(sc, 2)
    sc.setLogLevel("ERROR")
    scc.checkpoint(args.checkpoint)
    return scc

def filterUselessWords(word, blacklist):
    if word in blacklist:
        return False
    return True

## define the sorting fucntion for NEs
def appendToList(text, ner):
    if ner == "PERSON" and ' ' in text:
        people.append(text)
    elif ner == "LOCATION":
        locations.append(text)
    elif ner == "ORGANIZATION": 
        organisations.append(text)
    elif ner == "MISC":
        misc.append(text)
    elif ner == "DATE":
        dates.append(text)

## Entity Extraction function
def extractNER(sentence, nlpServer):
    # initialise lists for entities:
    people = []
    locations = []
    organisations = []
    dates = []
    misc = []

    # decode to UTF-8
    sentence_decode = sentence#.value.decode('utf-8')

    # pull out entities
    annotate_article = nlpServer.annotate(sentence_decode, properties={'annotators': 'ner', 'outputFormat': 'json'})
    for j in range(len(annotate_article['sentences'])):
        # reset the chamber per sentence
        chamber = []
        # iterate over tokens
        for k in range(len(annotate_article['sentences'][j]['tokens'])):

            token = annotate_article['sentences'][j]['tokens'][k]
            token_ner = token['ner']
            token_text = token['originalText']
           
            # this horrible chain of ifs and elses could be tidied up:
            if token_ner in [chamber[i][1] for i in range(len(chamber))]:
                chamber.append((token_text,token_ner))
            else:   
                if len(chamber) > 0:
                    appendPair = (' '.join([chamber[a][0] for a in range(len(chamber))]), chamber[0][1])
                    if appendPair[1] == "PERSON" and ' ' in appendPair[0]:
                        people.append(appendPair[0])
                    elif appendPair[1] == "LOCATION":
                        locations.append(appendPair[0])
                    elif appendPair[1] == "ORGANIZATION": 
                        organisations.append(appendPair[0])
                    elif appendPair[1] == "MISC":
                        misc.append(appendPair[0])
                    elif appendPair[1] == "DATE":
                        dates.append(appendPair[0])

                    ## reinitalise the chamber
                    chamber = []
                else:   
                    if token_ner in tokenlist:
                        chamber.append((token_text,token_ner))
                    else:   
                        pass
    return [people,locations,organisations,misc,dates]

## write a CSV file function:
def lineToCSV(line):
    return '|'.join(str(i) for i in line)

## Connect to NLP Server
nlp = StanfordCoreNLP(args.server)

# List Topics to pull out
tokenlist = ["PERSON","LOCATION","MISC","ORGANIZATION","DATE"]

wordBlacklist = ['', ' ', 'a', 'the', 'is', 'in', 'A', 'are','of','when','that','for','on', '|','as','to','The','an','and','News','-','with','at','it', 'has']

sc = SparkContext(appName='testing-python')

initialStateRDD = sc.parallelize([(u'test-data1', 1), (u'test-data2', 1)])

context = StreamingContext.getOrCreate(args.checkpoint, functionToCreateContext)

kvs = KafkaUtils.createDirectStream(context, [args.topic], {"metadata.broker.list": args.broker})

lines = kvs.map(lambda x: x[1])\
           .map(lambda line: line.split("|"))\
           .map(lambda x: x[0]) \
           .map(lambda line: extractNER(line, nlp))\
           .union\
           .map(lambda x: x[1]) \
           .map(lambda line: extractNER(line, nlp))\
           .union

lines.pprint()

#lines.saveAsTextFiles("/newsreader/csvs/test3.csv")

context.start()
context.awaitTermination()

'''
#def collocateWords(text):
#    tokens = word_tokenize(text)
#    return Text(tokens).collocations()
counts = lines.flatMap(lambda line: line.split(" ")) \
              .filter(lambda a: filterUselessWords(a,wordBlacklist)) \
              .map(lambda word: (word,1)) \
              .updateStateByKey(updateFunction, initialRDD=initialStateRDD)

#windowed = counts.window(60,slideDuration=30)
sortwords = counts.transform(lambda rdd: rdd.sortBy(lambda a: a[1], ascending=False))
sortwords.pprint()

context.start()
context.awaitTermination()

#counts.saveAsTextFiles("test",suffix="txt")
#######################################
############### Imports ############### 
#######################################
from kafka import KafkaProducer
from kafka import KafkaConsumer
from time import time
from datetime import timedelta
import datetime
from atexit import register
import argparse
from collections import Counter

############################################
############### Inital setup ############### 
############################################

# Parse command line arguments

parser = argparse.ArgumentParser(description="Read news articles from kafka topics and extract entities from text.")
parser.add_argument("kafka_broker", help="URL of the kafka broker in the form URL:PORT")
parser.add_argument("kafka_topic", help="kafka topic name to listen to")
parser.add_argument("-b", "--from-beginning", help="read from the beginning of the topic",
                            action="store_true", default=False)
parser.add_argument("-c", "--count", help="count the topN (given by -n) entities",
                            action="store_true", default=False)
parser.add_argument("-n", "--topn", help="show top n items",
                            action="store", type=int, default=10)
parser.add_argument("-t","--time", help="seconds to collect for",
                            action="store",type=int, default=0, required=False)
args = parser.parse_args()

## get topN
topN = args.topn

## define the 'ending' function
def Ending(kafka_consumer):
    kafka_consumer.close()
    if args.count == True:
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
        print("###############################")
        print('Dates:',Counter(dates).most_common(topN))


# start end timer
start = time()
if args.time > 0:
    timed = True
    end_time = datetime.datetime.now() + datetime.timedelta(seconds=args.time)
else:
    timed = False
    end_time = 0

# List Topics to pull out
tokenlist = ["PERSON","LOCATION","MISC","ORGANIZATION","DATE"]

# initalise buckets:
people = []
places = []
orgs = []
misc = []
dates = []

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

print("Listening....")
# read messages
while True:
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
               
                # this \/ horrible chain of ifs and elses could be tidied up:
                if token_ner in [chamber[i][1] for i in range(len(chamber))]:
                    chamber.append((token_text,token_ner))
                else:   
                    if len(chamber) > 0:
                        appendToList(' '.join([chamber[a][0] for a in range(len(chamber))]), chamber[0][1])
                        chamber = []
                    else:   
                        if token_ner in tokenlist:
                            chamber.append((token_text,token_ner))
                        else:   
                            pass

        if timed ==True and datetime.datetime.now() >= end_time:
            break
Ending(consumer)
'''

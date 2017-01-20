from pyspark import SparkContext
from pyspark import RDD
from pyspark import SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import *
import argparse
from pycorenlp import StanfordCoreNLP
import extractionFunctions
#from nltk import word_tokenize, Text, collocations

######### CLI arguments #########
parser = argparse.ArgumentParser()
parser.add_argument("broker")
parser.add_argument("topic")
parser.add_argument("-s", "--server", 
                    help="URL of the Stanford CoreNLP server (default: http://localhost:9000)",
                    action="store", required=True, default="http://localhost:9000")

args = parser.parse_args()

######### define functions ########

## write a CSV file function:
def lineToCSV(line):
    return '|'.join(str(i) for i in line)

## Connect to NLP Server
nlp = StanfordCoreNLP(args.server)

# List Topics to pull out
tokenlist = ["PERSON","LOCATION","MISC","ORGANIZATION","DATE"]

sc = SparkContext(appName='testing-python')
sc.setLogLevel("ERROR")
scc = StreamingContext(sc, 2)

kvs = KafkaUtils.createDirectStream(scc, [args.topic], {"metadata.broker.list": args.broker})

lines = kvs.map(lambda x: x[1])\
           .union(kvs.map(lambda x: x[1]).map(lambda line: line.split("|")[0])\
           .union(kvs.map(lambda x: x[1])\
           .map(lambda line: line.split("|")[1]))\
           .flatMap(lambda line: extractionFunctions.extractNER(line, nlp))\
           )

articles = kvs.map(lambda x: x[1])\

#.pprint(num=20)

scc.start()
scc.awaitTermination()

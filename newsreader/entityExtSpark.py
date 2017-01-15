from pyspark import SparkContext
from pyspark import RDD
from pyspark import SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import *
import argparse
#from nltk import word_tokenize, Text, collocations

######### CLI arguments #########
parser = argparse.ArgumentParser()
parser.add_argument("broker")
parser.add_argument("topic")
parser.add_argument("checkpoint")

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

def ExtractEntities(sentence):
    return

def collocateWords(text):
    tokens = word_tokenize(text)
    return Text(tokens).collocations()

wordBlacklist = ['', ' ', 'a', 'the', 'is', 'in', 'A', 'are','of','when','that','for','on', '|','as','to','The','an','and','News','-','with','at','it']

sc = SparkContext(appName='testing-python')

initialStateRDD = sc.parallelize([(u'test-data1', 1), (u'test-data2', 1)])

context = StreamingContext.getOrCreate(args.checkpoint, functionToCreateContext)

kvs = KafkaUtils.createDirectStream(context, [args.topic], {"metadata.broker.list": args.broker})

lines = kvs.map(lambda x: x[1])

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

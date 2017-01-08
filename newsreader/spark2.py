from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import *
import argparse

sc = SparkContext(appName='testing-python')
scc = StreamingContext(sc, 2)

parser = argparse.ArgumentParser()
parser.add_argument("broker")
parser.add_argument("topic")

args.parser.parse_args()

kvs = KafkaUtils.createDirectStream(scc, [args.topic], {"metadata.broker.list": args.broker})
lines = kvs.map(lambda x: x[1])
counts = lines.flatMap(lambda line: line.split(" ")) \
        .map(lambda word: (word,1)) \
        .reduceByKey(lambda a, b: a+b)
counts.pprint()

scc.start()
scc.awaitTermination()


#totals = counts.window(Seconds(10)).countByValue()
#totals.pprint()

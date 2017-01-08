from pyspark import SparkContext
from pyspark import RDD
from pyspark import SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import *
import argparse

sc = SparkContext(appName='testing-python')
scc = StreamingContext(sc, 2)
sc.setLogLevel("ERROR")

parser = argparse.ArgumentParser()
parser.add_argument("broker")
parser.add_argument("topic")

args = parser.parse_args()

initialStateRDD = sc.parallelize([(u'test-data1', 1), (u'test-data2', 1)])

kvs = KafkaUtils.createDirectStream(scc, [args.topic], {"metadata.broker.list": args.broker})
lines = kvs.map(lambda x: x[1])

#lines.pprint(num=40)

counts = lines.flatMap(lambda line: line.split(" ")) \
        .map(lambda word: (word,1)) \
        .reduceByKey(lambda a, b: a+b)\
        .sortByKey(lambda _,a: a)

windowed = counts.window(60,slideDuration=30)

output = windowed.foreachRDD(counts.sortByKey(lambda b: b))
output.pprint()

#windowed = counts.window(60,slideDuration=30).pprint(num=50)
#sortWindow = windowed.transform(sortByKey(lambda a, b: b))
#sortWindow.pprint(num=20)

#counts.saveAsTextFiles("test",suffix="txt")
#counts.pprint(num=30)

scc.start()
scc.awaitTermination()

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import *

sc = SparkContext(appName='testing-python')
scc = StreamingContext(sc, 2)

brokers = 'localhost:9092'
topic = 'python-test'

kvs = KafkaUtils.createDirectStream(scc, [topic], {"metadata.broker.list": brokers})
lines = kvs.map(lambda x: x[1])
counts = lines.flatMap(lambda line: line.split(" ")) \
        .map(lambda word: (word,1)) \
        .reduceByKey(lambda a, b: a+b)
totals = counts.window(Seconds(10)).countByValue()
totals.pprint()
#counts.pprint()

scc.start()
scc.awaitTermination()

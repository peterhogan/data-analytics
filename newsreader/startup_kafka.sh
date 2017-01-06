#!/bin/bash
#logfilename: /tmp/startupkafka.log

/root/zookeeper-3.4.9/bin/zkServer.sh start &> /tmp/startupkafka.log
echo "Zookeeper started. Now starting Kafka"
/root/kafka_2.11-0.10.1.0/bin/kafka-server-start.sh /root/kafka_2.11-0.10.1.0/config/server.properties &> /tmp/startupkafka.log
echo "Script Finished..."

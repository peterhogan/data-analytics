#!/bin/bash
LOG_FILE=/tmp/kafka_start.log
/opt/zookeeper-3.4.9/bin/zkServer.sh start &>> $LOG_FILE
/opt/kafka_2.11-0.10.1.1/bin/kafka-server-start.sh /opt/kafka_2.11-0.10.1.1/config/server.properties &>> $LOG_FILE
/opt/kafka_2.11-0.10.1.1/bin/kafka-topics.sh --zookeeper localhost:2181 --create --topic newsreader --partitions 1 --replication-factor 1 &>> $LOG_FILE

from optparse import OptionParser

kafkabroker = ""
kafkatopic = ""
rssfile = ""

helpstring = """Usage: newsreader.py [OPTIONS]... -f <RSS_FILE> <KAFKA_BROKER> <KAFKA_TOPIC>

Read news articles from XML rss feeds specified in <RSS_FILE>
Feeds must be separated by newlines
Feeds to be ignored can be prefixed with #

Mandatory arguments:
    -f, --rssfile       path to rss feeds file (.xml URLs)

Optional arguments:
    -q, --quiet         don't print the GUID of every article read (default off)
    -l, --live          print a running total of how many articles have been sent (default off)
    -w, --wait          wait for a carriage return before sending to kafka (default off)
    -h, --help          print this message

Example: newsreader.py -q -f /data/rssfeeds.txt localhost:9092 topic_1
"""
parser = OptionParser()
parser.add_option("-f", "--file",
                  

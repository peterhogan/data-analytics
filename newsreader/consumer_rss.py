#######################################
############### Imports ############### 
#######################################
from kafka import KafkaProducer
from kafka import KafkaConsumer
from time import time
from datetime import timedelta
from atexit import register
from pycorenlp import StanfordCoreNLP

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
args = parser.parse_args()

## define the 'ending' function
def Ending(kafka_consumer):
    kafka_consumer.close()
    print('Time taken:', str(timedelta(seconds=time()-start)))
    print('Messages received:', filesread)

# start timer
start = time()

###################################
######### Start Receiving ######### 
###################################

# define the counter variables:
filesread = 0

# start the kafka consumer
consumer = KafkaConsumer(args.kafka_topic
                         bootstrap_servers=[args.kafka_broker])

# register the exit code
register(Ending,consumer)

# open the port to the NLP server
nlp = StanfordCoreNLP(args.server)

# read messages
for msg in consumer:
    filesread += 1

from pycorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('http://172.17.0.1:9000')

articlelist =['Theresa May is going to fire David Cameron', 'Mike Smith is going to France','The US president Barack Obama has said Donald Trump is a knobber', 'Mike Jordan Smith, David Cameron and Michelle Obama went to the French capital Paris, in April']

people = []
places = []
orgs = []
misc = []

tokenlist = ["PERSON","LOCATION","MISC","ORGANISATION"]

def appendToList(text, ner):
    if ner == "PERSON":
        people.append(text)
    elif ner == "LOCATION":
        places.append(text)
    elif ner == "ORGANISATION":
        orgs.append(text)
    elif ner == "MISC":
        misc.append(text)

for article in articlelist:
    annotate_article = nlp.annotate(article, properties={'annotators': 'ner', 'outputFormat': 'json'})
    for j in range(len(annotate_article['sentences'])):
        tokens_in_sequence = 0
        for token in annotate_article['sentences'][j]['tokens']:
            token_ner = token['ner']
            if token_ner in tokenlist:
                token_text = token['originalText']
                appendToList(token_text, token_ner)

print('People:',people)
print('Places:',places)
print('Organisations:',orgs)
print('Misc:',misc)

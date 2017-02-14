############### Imports ############### 
import argparse
import logging
import word2vec as w2v
from time import time

############### Inital setup ############### 

# Parse command line arguments

parser = argparse.ArgumentParser(description="test")

parser.add_argument("input", help="file to parse")

parser.add_argument("-q", "--quiet", help="log level WARN",
                    action="store_true", default=False)
parser.add_argument("-v", "--verbose", help="log level DEBUG",
                    action="store_true", default=False)
cli = parser.parse_args()

# Logging
if cli.quiet:
    logging.basicConfig(level=logging.ERROR)
elif cli.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

log = logging.getLogger(name='filelog')

# Word2Vec

running = True

temp_phrases = '/tmp/phrases'
temp_bin = '/tmp/word2vec.bin'
temp_clusters = '/tmp/clusters.txt'

start = time()

w2v.word2phrase(cli.input,temp_phrases, verbose=False)
w2v.word2vec(temp_phrases, temp_bin, size=500, verbose=False)
w2v.word2clusters(cli.input, temp_clusters, 500, verbose=False)

model = w2v.load(temp_bin)

end = time()

print("process time taken", end - start)

while running == True:
    print("""what would you like to do?
    1. word/phrase response
    2. analogies
    3. quit""")
    while True:
        try:
            response = int(input(">> "))
            break
        except (ValueError,TypeError):
            print('please type a number')

    if response == 1:
        print("what is your query?")
        while True:
            try:
                query = str(input(">> "))
                break
            except (ValueError,TypeError):
                print('please type a valid query')
        try:
            ind, met = model.cosine(query)
        except KeyError:
            print('Error')
            continue

    elif response == 2:
        print("list positive words")
        while True:
            try:
                posi = str(input(">> "))
                break
            except (ValueError,TypeError):
                print('please type a valid string')
        print("list negative words")
        while True:
            try:
                negi = str(input(">> "))
                break
            except (ValueError,TypeError):
                print('please type a valid string')
        try:
            ind, met= model.analogy(pos=posi.split(" "), neg=negi.split(" "), n=10)
        except KeyError:
            print("Error")
            continue

    elif response == 3:
        quit()

    else:
        quit()

    word_out = model.generate_response(ind, met).tolist()

    for i in word_out:
        print(i[0], "- relevance:",i[1])

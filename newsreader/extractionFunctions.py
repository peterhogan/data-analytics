from pycorenlp import StanfordCoreNLP

######### define functions ########

## write a CSV file function:
def lineToCSV(line):
    return '|'.join(str(i) for i in line)

# List Topics to pull out
tokenlist = ["PERSON","LOCATION","MISC","ORGANIZATION","DATE"]

## define the sorting fucntion for NEs
def appendToList(text, ner):
    if ner == "PERSON" and ' ' in text:
        people.append(text)
    elif ner == "LOCATION":
        locations.append(text)
    elif ner == "ORGANIZATION": 
        organisations.append(text)
    elif ner == "MISC":
        misc.append(text)
    elif ner == "DATE":
        dates.append(text)

## Entity Extraction function
def extractNER(sentence, nlpServer):
    # initialise list for entities:
    entities = []

    # decode to UTF-8
    sentence_decode = sentence#.value.decode('utf-8')

    # pull out entities
    annotate_article = nlpServer.annotate(sentence_decode, properties={'annotators': 'ner', 'outputFormat': 'json'})
    for j in range(len(annotate_article['sentences'])):
        # reset the chamber per sentence
        chamber = []
        # iterate over tokens
        for k in range(len(annotate_article['sentences'][j]['tokens'])):

            token = annotate_article['sentences'][j]['tokens'][k]
            token_ner = token['ner']
            token_text = token['originalText']
           
            # this horrible chain of ifs and elses could be tidied up:
            if token_ner in [chamber[i][1] for i in range(len(chamber))]:
                chamber.append((token_text,token_ner))
            else:   
                if len(chamber) > 0:
                    appendPair = (chamber[0][1],' '.join([chamber[a][0] for a in range(len(chamber))])) 
                    entities.append(appendPair)

                    ## reinitalise the chamber
                    chamber = []
                else:   
                    if token_ner in tokenlist:
                        chamber.append((token_text,token_ner))
                    else:   
                        pass

    return list(set(entities))

## Entity Extraction function
def encodeNER(text, entities, delim=" || "):
    #initalise node dictionary
    article  = {}

    # separate the variables
    split_text = text.split(delim)

    # ordered list of fields to map to node
    fields = ['title','description','published','guid','reportedby']

    # map values to fields
    for i,f in zip(range(len(fields)),fields):
        article[f]=split_text[i]

    # construct entity dictionaries
    ents = []
    for ent in sorted(list(set([i[0] for i in entities if entities]))):
        itr = 1
        values = []
        for val in sorted([j for (i,j) in entities if i == ent]):
            values.append((ent+str(itr),val)) 
            itr += 1
        ents.append((ent+'S',dict(values)))

    node = article.copy()
    node.update(dict(ents))

    return node

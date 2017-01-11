from pycorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('http://172.17.0.1:9000')

articlelist =['Theresa May is going to fire David Cameron', 'Mike Smith is going to France','The US president Barack Obama has said Donald Trump is a knobber', 'Mike Jordan Smith, David Cameron and Michelle Obama went to the French capital Paris, in April']

people = []
places = []

for article in articlelist:
    annotate_article = nlp.annotate(article, properties={'annotators': 'ner', 'outputFormat': 'json'})
    for j in range(len(annotate_article['sentences'])):
        #print(annotate_article['sentences'][j])
        for token in annotate_article['sentences'][j]['tokens']:
            if token['ner'] == 'O':
                pass
                #print(token['originalText']+':',token['ner'])
            if token['ner'] == 'PERSON':
                people.append(token['originalText'])
            if token['ner'] == 'LOCATION':
                places.append(token['originalText'])

print('People:',people)
print('Places:',places)

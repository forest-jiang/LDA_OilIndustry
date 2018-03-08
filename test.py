__author__ = 'forestj'

filename = 'OilPriceArticles2014_headlines.csv'
#filename = 'SMALL.csv'

# U for universal return character

from gensim import corpora
with open (filename, 'rU') as f:
    dictionary = corpora.Dictionary(line.strip().split() for line in f.readlines())

# Need to remove punctual and "

with open('stopwords.txt','rU') as f:
    stoplist = f.readlines()
    stoplist = set([word.strip() for word in stoplist])


class MyCorpus(object):
    def __iter__(self):
        for line in open(filename, 'rU').readlines():
            doc = [word for word in line.strip().split() if word not in stoplist]
            yield dictionary.doc2bow(doc)

class MyCorpus_txt(object):
    def __iter__(self):
        for line in open(filename, 'rU').readlines():
            yield line

# Number of topics
K = 20
from gensim import models
lda = models.ldamodel.LdaModel(corpus = MyCorpus(), id2word = dictionary,
                               num_topics = K, update_every = 1,
                               chunksize = 100000, passes = 3)

print "Topics found:"
print "\n".join(lda.show_topics(K, num_words=50,formatted=True))


# Print some documents and its topic attributes
documents_bow = [doc for doc in MyCorpus()]
documents_txt = [doc for doc in MyCorpus_txt()]

n_doc = 10
for i in range(n_doc):
    print documents_txt[i]
    print lda[documents_bow[i]]


import pyLDAvis.gensim

pyLDAvis.gensim.prepare(lda, corpus, dictionary)
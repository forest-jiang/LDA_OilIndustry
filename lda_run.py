__author__ = 'forestj'
import numpy as np
import os
########################## Input parameters #######################################

# Input files
input_file = 'OilPriceArticles2014_Headlines_Only_cleaned.csv'
input_file = 'Oil_Price_Articles_2000_2015_HeaderAndFP_furtherRmv.csv'
input_file = '1970-2016_Art_cleaned.csv'
input_file = '1970-2016NEW_art_cleaned.csv'

input_file = '2015-2016NEW_art_cleaned.csv'


stopword_file = 'stopwords_merged.txt'

# Output folder
output_folder = './oilPricesSince1970_topic10_2/'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Output files for visualization
out_dict_file = output_folder+'out_vocab.txt'
out_doc_length = output_folder+'out_doc_len.txt'
out_word_freq = output_folder+'out_word_freq.txt'
out_topics_word_dist = output_folder+'out_topics_word_dist.txt'
out_docs_topics_dist = output_folder+'out_docs_topics_dist.txt'

# Output files for easy reading
out_easy_topics = output_folder+'out_easy_topics.csv'
out_easy_topics_sorted = output_folder+'out_easy_topics_sorted.csv'
out_easy_docs   = output_folder+'out_easy_docs.csv'


# Number of topics
K = 10

# W
num_word_show_topic = 1e6

# Some notes
# U for universal return character
# Need to remove punctual and " (Mustafa working on that)





########################## Build up the dictionary ################################
# Read the stopword list
with open(stopword_file,'r') as f:
    stoplist = f.readlines()
    stoplist = set([word.strip() for word in stoplist])

# # For test all the documents
# with open (input_file, 'r') as f:
#     alllines= f.readlines() # For each document, remove stop words
#     alllines = [line.decode("utf-8").replace(u'\u2019',"'") for line in alllines]

doc_lengths = []
word_freq = dict()
# Build up the dictionary, use the stemmer
import nltk
stemmer = nltk.PorterStemmer()
from gensim import corpora
with open (input_file, 'r') as f:
    dictionary = corpora.Dictionary()
    for line in f.readlines(): # For each document, remove stop words
        lineReg = line.decode('utf-8')
        doc_as_word_list = [stemmer.stem(word) for word in lineReg.strip().split() if word not in stoplist]
        dictionary.add_documents([doc_as_word_list])
        doc_lengths.append(len(doc_as_word_list))

        for word in doc_as_word_list:
            word_freq[word] =word_freq.get(word,0) + 1


# Output the dictionary (vocab)
f = open(out_dict_file,'w')
dictionary_keys = dictionary.keys()
dictionary_keys.sort()
for key in dictionary_keys:
    f.write((dictionary[key]+'\n').encode('utf-8'))
f.close()

# Output the document length
f = open(out_doc_length,'w')
for doc_length in doc_lengths:
    f.write(str(doc_length)+'\n')
f.close()

# Output the word frequency
f = open(out_word_freq,'w')
for key in dictionary_keys:
    f.write(str(word_freq[dictionary[key]])+'\n')
f.close()

num_words_in_dict = len(dictionary_keys)
num_docs = dictionary.num_docs
########################## LDA algorithm ##########################################

# The class that yields one document at a time, as a bag-of-words
class MyCorpus(object):
    def __iter__(self):
        for line in open(input_file, 'rU').readlines():
            lineReg = line.decode('utf-8')
            doc_as_word_list = [word for word in lineReg.strip().split() if word not in stoplist]
            yield dictionary.doc2bow(doc_as_word_list)

# The class that yields one document at a time, as a long string
class MyCorpus_txt(object):
    def __iter__(self):
        for line in open(input_file, 'rU').readlines():
            yield line

# Main lda
from gensim import models
lda = models.ldamodel.LdaModel(corpus = MyCorpus(), id2word = dictionary,
                               num_topics = K, update_every = 0,
                               passes = 20)
#                               chunksize = 100

############################ Output ###############################################


# Output of topics
f = open(out_topics_word_dist,'w')
for iTopic in range(K):
    topics = lda.show_topic(iTopic,num_word_show_topic)
    word_dist = np.zeros(num_words_in_dict)
    for p_word, word in topics:
        word_dist[dictionary.token2id[word]] = p_word
    for keys in dictionary_keys:
        f.write(str(word_dist[keys])+' ')
    f.write('\n')
f.close()


global_topic_weights = np.zeros(K)
# Output of documents
f = open(out_docs_topics_dist,'w')
# for iDoc in range(num_docs):
for doc in MyCorpus():
    doc_topics = lda.get_document_topics(doc,0)
    for iTopic in range(K):
        global_topic_weights[iTopic] += doc_topics[iTopic][1]
        f.write(str(doc_topics[iTopic][1])+' ')
    f.write('\n')
f.close()


# Output files for easy reading
topic_global_sorted_ind = np.argsort(global_topic_weights)
f = open(out_easy_topics_sorted,'w')
for iTopic in topic_global_sorted_ind[::-1]:
    f.write('Topic weight: ' + str(global_topic_weights[iTopic])+', ')
    f.write((lda.print_topic(iTopic, 50)+'\n').encode('utf-8'))
f.close()

f = open(out_easy_topics,'w')
for iTopic in range(K):
    f.write('Topic weight: ' + str(global_topic_weights[iTopic])+', ')
    f.write((lda.print_topic(iTopic, 50)+'\n').encode('utf-8'))
f.close()


documents_bow = [doc for doc in MyCorpus()]
documents_txt = [doc for doc in MyCorpus_txt()]
f = open(out_easy_docs,'w')
for iDoc in range(num_docs):
    f.write(documents_txt[iDoc])
    top_dist_in_doc = lda.get_document_topics(documents_bow[iDoc],minimum_probability=1.0/K+0.001)
    for iTopic,topic_weight in top_dist_in_doc:
        f.write(str(iTopic)+': '+'%.4f'%topic_weight+', ')
    f.write('\n')
f.close()




# Print some documents and its topic attributes
n_doc = 10
for i in range(n_doc):
    print documents_txt[i]
    print lda[documents_bow[i]]


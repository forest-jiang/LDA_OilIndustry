__author__ = 'forestj'
import numpy as np
import os
import time
import re
start_time = time.time()

########################## Input parameters #######################################

# Input files
input_file = 'petrowiki765_lower.csv'
year_file = ''
stopword_file = 'stopwords.txt'

# Output folder
output_folder = './petrowiki765_lower/'

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
out_easy_docs_top_topic   = output_folder+'out_easy_docs_top.csv'
out_easy_docs_alltopics   = output_folder+'out_easy_docs_all.csv'

# Output files for multiline vis
out_topic_trend = output_folder+'topics_line_vis.tsv'

# Other out files
out_log_file = output_folder+'lda_log.txt'
out_lda_save = output_folder+'lda_save'

# Whether to reload
reload_lda = False

# Number of topics
K = 10

# Number of words in topics for multiline visualization
n_words_topic = 10

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
import logging
logging.basicConfig(filename=out_log_file,level=logging.DEBUG)

# The class that yields one document at a time, as a bag-of-words, again, stemmed
class MyCorpus(object):
    def __iter__(self):
        for line in open(input_file, 'rU').readlines():
            lineReg = line.decode('utf-8')
            doc_as_word_list = [stemmer.stem(word) for word in lineReg.strip().split() if word not in stoplist]
            yield dictionary.doc2bow(doc_as_word_list)

class MyCorpus_rand(object):
    def __iter__(self):
        all_lines = open(input_file, 'rU').readlines()
        for i_doc in np.random.permutation(len(all_lines)):
            lineReg = all_lines[i_doc].decode('utf-8')
            doc_as_word_list = [stemmer.stem(word) for word in lineReg.strip().split() if word not in stoplist]
            yield dictionary.doc2bow(doc_as_word_list)

# The class that yields one document at a time, as a long string
class MyCorpus_txt(object):
    def __iter__(self):
        for line in open(input_file, 'rU').readlines():
            yield line

class MyCorpus_word_list_stemmed(object):
    def __iter__(self):
        for line in open(input_file, 'rU').readlines():
            yield [stemmer.stem(word) for word in line.decode('utf-8').strip().split() if word not in stoplist]

# Main lda
from gensim import models
if reload_lda:
    lda = models.ldamodel.LdaModel.load(out_lda_save)
else:
    lda = models.ldamodel.LdaModel(corpus = MyCorpus_rand(), id2word = dictionary,
                                   num_topics = K, update_every = 0,
                                   passes = 10)
    lda.save(out_lda_save)
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
f = open(out_easy_docs_top_topic,'w')
for iDoc in range(num_docs):
    f.write(documents_txt[iDoc])
    top_dist_in_doc = lda.get_document_topics(documents_bow[iDoc],minimum_probability=1.0/K+0.001)
    for iTopic,topic_weight in top_dist_in_doc:
        f.write(str(iTopic)+': '+'%.4f'%topic_weight+', ')
    f.write('\n')
f.close()

f = open(out_easy_docs_alltopics,'w')
f.write(','.join(lda.print_topics(num_words=10))+',Document\n')
for iDoc in range(num_docs):
    top_dist_in_doc = lda.get_document_topics(documents_bow[iDoc],minimum_probability=0.0)
    assert(len(top_dist_in_doc)==K)
    for (i_topic,topic_weight_tuple) in enumerate(top_dist_in_doc):
        assert(i_topic==topic_weight_tuple[0])
        f.write('%.5f'%topic_weight_tuple[1]+',')
    if len(documents_txt[iDoc]) > 5001:
        f.write(documents_txt[iDoc][:5000])
        f.write('\n')
    else:
        f.write(documents_txt[iDoc])
f.close()



# Read topic distribution per article
with open (out_docs_topics_dist, 'r') as f:
    all_lines = f.readlines()

all_topic_dist = []
for line in all_lines:
    all_topic_dist.append([float(val) for val in line.split()])

all_topic_dist = np.array(all_topic_dist)
n_topics = all_topic_dist.shape[1]

if len(year_file)>0:
    # Read year data
    with open (year_file, 'r') as f:
        all_years = f.readlines()
    years = [int(str) for str in all_years]
    unique_years = np.unique(years)

    # Read words for each topics
    with open(out_easy_topics,'r') as f:
        all_lines = f.readlines()
    p = re.compile(r'\*(\w*)')
    words_in_topic = []
    for line in all_lines:
        words_in_topic.append(p.findall(line)[:n_words_topic])

    # Denomitator for Normalization
    den = dict()
    for year in unique_years:
        index_this_year = (years==year).nonzero()[0]
        den[year]= np.sum(all_topic_dist[index_this_year,])


    # output the trend TSV file
    f = open(out_topic_trend,'w')
    f.write('words\t'+'\t'.join([np.str(val) for val in unique_years])+'\n')
    for itopic in range(n_topics):
        f.write(' '.join(words_in_topic[itopic]))
        for year in unique_years:
            index_this_year = (years==year).nonzero()[0]
            f.write('\t'+ np.str(np.sum(all_topic_dist[index_this_year,itopic])/den[year]))
        f.write('\n')

    f.close()



print("--- %s seconds ---" % (time.time() - start_time))
start_time = time.time()
output_folder_stripped = ''.join([i for i in output_folder if i not in {'.','/','\\'}])

os.system('copy visualizinginprog.R .\\'+output_folder_stripped+'\\')

pwd= os.getcwd()
os.chdir(output_folder)
print('Running R script')
os.system('rscript visualizinginprog.R')
os.chdir(pwd)
print("--- %s seconds ---" % (time.time() - start_time))
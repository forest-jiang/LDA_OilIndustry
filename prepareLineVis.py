__author__ = 'forestj'
import numpy as np
import re
########################## Input files #######################################

# Main parameters to change
project_folder = './oilPricesSince1970_topic20/'
year_file = '1970-2016NEW_year.csv'
# Number of words in topics
n_words_topic = 10


dist_file = project_folder+'out_docs_topics_dist.txt'
topic_word_file = project_folder+'out_easy_topics.csv'
out_topic_trend = project_folder+'topics_line_vis.tsv'


# Read topic distribution per article
with open (dist_file, 'r') as f:
    all_lines = f.readlines()

all_topic_dist = []
for line in all_lines:
    all_topic_dist.append([float(val) for val in line.split()])

all_topic_dist = np.array(all_topic_dist)
n_topics = all_topic_dist.shape[1]

# Read year data
with open (year_file, 'r') as f:
    all_years = f.readlines()
years = [int(str) for str in all_years]
unique_years = np.unique(years)

# Read words for each topics
with open(topic_word_file,'r') as f:
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

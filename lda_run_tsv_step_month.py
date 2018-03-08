__author__ = 'forestj'
import numpy as np
import os
import time
import re
start_time = time.time()

########################## Input parameters #######################################

# Input files
# year_file = '../New York Times Downloader/All Articles 2 Everyday Complete/YearAll_Articles.csv'
# month_file = '../New York Times Downloader/All Articles 2 Everyday Complete/MonthAll_Articles.csv'
year_file = '1970-2016NEW_year.csv'
month_file = '1970-2016_month.csv'


# Output folder
# output_folder = 'Q:/Students/Folake/AllArticles_topic50_stem/'
output_folder = './oilPricesSince1970_topic10_stemmed2/'

tsv_output_path_name = './oilPricesArticles_topic10_monthly.tsv'

# year_file = '../New York Times Downloader/Oil Articles/Originals/YearOilArticles.csv'
# month_file = '../New York Times Downloader/Oil Articles/Originals/MonthOilArticles.csv'
# output_folder = 'Q:/Students/Folake/OilArticles_topic20_stem/'
# tsv_output_path_name = './OilArticles_topic20_monthly.tsv'

# Output files for visualization
out_dict_file = output_folder+'out_vocab.txt'
out_doc_length = output_folder+'out_doc_len.txt'
out_word_freq = output_folder+'out_word_freq.txt'
out_topics_word_dist = output_folder+'out_topics_word_dist.txt'
out_docs_topics_dist = output_folder+'out_docs_topics_dist.txt'


# # Output files for easy reading
out_easy_topics = output_folder+'out_easy_topics.csv'
# out_easy_topics_sorted = output_folder+'out_easy_topics_sorted.csv'
# out_easy_docs_top_topic   = output_folder+'out_easy_docs_top.csv'
# out_easy_docs_alltopics   = output_folder+'out_easy_docs_all.csv'

# Output files for multiline vis
out_topic_trend = tsv_output_path_name  #output_folder+'topics_line_vis.tsv'
#
# # Number of topics
# K = 10
#
# Number of words in topics for multiline visualization
n_words_topic = 10
#
# # W
# num_word_show_topic = 1e6

# Some notes
# U for universal return character
# Need to remove punctual and " (Mustafa working on that)

# Read topic distribution per article
with open (out_docs_topics_dist, 'r') as f:
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
# Read month data
with open (month_file, 'r') as f:
    all_months = f.readlines()
months = list(years)
for i,s in enumerate(all_months):
    if s[0] is not '#':
        months[i] = int(s)
    else:
        months[i] = months[i-1]

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
    for month in range(1,13):
        index_this_year_month = ((np.array(years)==year) & (np.array(months)==month)).nonzero()[0]
        den[year*100+month]= np.sum(all_topic_dist[index_this_year_month,])


# output the trend TSV file
f = open(out_topic_trend,'w')
year_month_labels =[]
for year in unique_years:
        for month in range(1,13):
            if den[year*100+month] != 0.0:
                year_month_labels.append(np.str(year*100+month))
f.write('words\t'+'\t'.join(year_month_labels)+'\n')
for itopic in range(n_topics):
    f.write(' '.join(words_in_topic[itopic]))
    for year in unique_years:
        for month in range(1,13):
            if den[year*100+month] != 0.0:
                index_this_year_month = ((np.array(years)==year) & (np.array(months)==month)).nonzero()[0]
                f.write('\t'+ np.str(np.sum(all_topic_dist[index_this_year_month,itopic])/den[year*100+month]))
    f.write('\n')

f.close()


print("--- %s seconds ---" % (time.time() - start_time))
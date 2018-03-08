#writing stop words to file 
# write.table(stop_words, file = "stop_wordsxtra.txt", append = FALSE, quote = FALSE, sep = " ",
#             +             eol = "\n", na = "NA", dec = ".", row.names = FALSE,
#             +             col.names = FALSE, qmethod = c("escape", "double"),
#             +             fileEncoding = "")

setwd(".\\")
library(LDAvis)
doc.length<-read.table("out_doc_len.txt", header=FALSE, sep="" )
doc.len=doc.length[,1]
vocab<-read.table("out_vocab.txt", header =FALSE,colClasses="character", sep="\t", fill=FALSE, strip.white=TRUE ,quote ='')
vocabular=vocab[,1]
term.frequency<-read.table("out_word_freq.txt", header =FALSE)
term.freq=term.frequency[,1]
theta<-read.table("out_docs_topics_dist.txt", header =FALSE)
phi<-read.table("out_topics_word_dist.txt", header =FALSE)


json <- createJSON(phi = phi, theta = theta, vocab = vocabular, doc.length = doc.len, term.frequency = term.freq)
serVis(json, out.dir = "vista3", open.browser = FALSE)

##


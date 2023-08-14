import logging, gensim, bz2
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# load id->word mapping (the dictionary), one of the results of step 2 above
id2word = gensim.corpora.Dictionary.load_from_text('wiki_lsa_wordids.txt')
# load corpus iterator
mm = gensim.corpora.MmCorpus('wiki_lsa_tfidf.mm')
print(mm)

# extract 400 LSI topics; use the default one-pass algorithm
lsi = gensim.models.lsimodel.LsiModel(corpus=mm, id2word=id2word, num_topics=400)
lsi.print_topics(10)

lsi.save('model.lsi')


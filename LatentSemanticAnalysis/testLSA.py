import logging, gensim, bz2

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# load id->word mapping (the dictionary), one of the results of step 2 above
dictionary = gensim.corpora.Dictionary.load_from_text('wiki_lsa_wordids.txt')

words= dictionary.token2id.keys()
import cPickle as pickle
file=open("LSAWords.pickle","wb")
print len(words)
pickle.dump(words,file)
file.close()

# load lsi model
lsi = gensim.models.LsiModel.load("model.lsi")

# get word index
#termcorpus=gensim.matutils.Dense2Corpus(lsi.projection.u.T) 
#index = gensim.similarities.MatrixSimilarity(termcorpus) 
#index.save('words.index')
index = gensim.similarities.MatrixSimilarity.load('words.index')


def printsims(query):
	# get cosine similarity of the query to each one of the 12 terms
	sims = index[query]
	sorted_sims = sorted(enumerate(sims), key=lambda item: -item[1])
	# print the result, converting ids (integers) to words (strings)
	fmt = ["%s(%f)" % (dictionary[idother], sim) for idother, sim in sorted_sims[:10]]
	print "the query is similar to"
	print ', '.join(fmt) 


while True:
	doc = raw_input("Input: ")
	vec_bow = dictionary.doc2bow(doc.lower().split())
	vec_lsi = lsi[vec_bow] # convert the query to LSI space
	print "LSA coordinates:"
	print(vec_lsi[:5])
	printsims(vec_lsi)
	print("\n")


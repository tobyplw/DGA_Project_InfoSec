import gensim.downloader as api
import pickle


#create word2vec_model
print("Creating Word2Vec Model")
word2vec_model = api.load('word2vec-google-news-300')
pickle.dump(word2vec_model, open("word2vec_model.pickle", "wb"))
print("Word2Vec model has been created")




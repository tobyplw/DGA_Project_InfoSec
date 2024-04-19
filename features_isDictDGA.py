import re
import pandas as pd
import numpy as np
from collections import Counter
import gensim.downloader as api
import wordninja
import nltk
import pickle

#make sure these dependencies are downloaded
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
print("Loading Word2Vec Model")

#open up word2Vec model
word2vec_model = pickle.load(open("word2vec_model.pickle", "rb"))
print("Finished")

# https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
noun_list = ["NN", "NNS", "NNP", "NNPS"]
verb_list = ["VB", "VBD", "VBG", "VBN", "VPZ","VBZ"]
adverb_list = ["RB", "RBR", "RBS"]
adjectives_list = ["JJ", "JJR", "JJS"]
combined_list = noun_list + verb_list + adverb_list + adjectives_list 

#split domain into list of words using wordninja
def split_words(domain):
    stripped_domain = domain.split(".")[0]
    return wordninja.split(stripped_domain)

#exctract the Part of Speech for a given word
def extract_POS(words):
    return nltk.pos_tag(words)

#calculate the number of noun in a word list
def number_of_nouns(words):
    nouns = 0
    for word in words:
        pos = word[1]
        if pos in noun_list:
            nouns+=1
    return nouns

#calculate the number of verbs in a word list
def number_of_verbs(words):
    verbs = 0
    for word in words:
        pos = word[1]
        if pos in verb_list:
            verbs+=1
    return verbs

#calculate the number of adverbs in a word list
def number_of_adverbs(words):
    adverbs = 0
    for word in words:
        pos = word[1]
        if pos in adverb_list:
            adverbs+=1
    return adverbs

#calculate the number of adjectives in a word list
def number_of_adjectives(words):
    adjectives = 0

    for word in words:
        pos = word[1]
        if pos in adjectives_list:
            adjectives+=1
    return adjectives

#calculate the number of Others (not noun, verb, adverb, adjective) in a word list
def number_of_others(words):
    others = 0
    for word in words:
        pos = word[1]
        if pos not in combined_list:
            others+=1
    return others

#get all the counts for a row
def get_POS_Counts(row):
    nouns = row['num_nouns']
    verbs = row['num_verbs']
    adverbs = row['num_adverbs']
    adjectives = row['num_adjectives']
    others = row['num_others']
    return {"nouns": nouns,"verbs" : verbs, "adverbs" : adverbs, "adjectives" : adjectives, "others" : others}

#calculate ratios between all the different POS tags
def POS_ratio(counts, type):
    total = 0
    for value in counts.values():
        total += value
    
    if type == "nouns":
        return counts["nouns"] / total
    if type == "verbs":
        return counts["verbs"] / total
    if type == "adverbs":
        return counts["adverbs"] / total
    if type == "adjectives":
        return counts["adjectives"] / total
    if type == "others":
        return counts["others"] / total

#calculate the average similiarity between all words in a word list
def similarity_avg(words):
    total_similiarity = 0
    total_combos = 0
    if len(words) == 0:
        return 0
    if len(words) == 1:
        return 1
    
    for i in range(len(words)):
        for j in range(i + 1, len(words)):
            try:
                #get similiary from word2vec_model
                similarity = word2vec_model.similarity(words[i], words[j])
            except KeyError:
                similarity = 0
            #print(f"Similarity between '{words[i]}' and '{words[j]}': {similarity}")
            total_similiarity+=similarity
            total_combos+=1
    
    #calcilate average
    average_similiarity = total_similiarity / total_combos
    return average_similiarity

#extract features from either a singular domain, or a data_frame
def extract_features(domain = "", data_frame = None):
    if data_frame is None:
        d = {'domain': [domain]}
        features = pd.DataFrame(data=d)
    else:
        features = data_frame
    
    features['split_words'] = features.domain.apply(split_words)
    features['POS'] = features.split_words.apply(extract_POS)
    features['num_nouns'] = features.POS.apply(number_of_nouns)
    features['num_verbs'] = features.POS.apply(number_of_verbs)
    features['num_adverbs'] = features.POS.apply(number_of_adverbs)
    features['num_adjectives'] = features.POS.apply(number_of_adjectives)
    features['num_others'] = features.POS.apply(number_of_others)

    for index, row in features.iterrows():
        counts = get_POS_Counts(row)
        features.at[index, 'similarity_avg'] = similarity_avg(row['split_words'])
        features.at[index, 'noun_ratio'] = POS_ratio(counts, "nouns")
        features.at[index, 'verb_ratio'] = POS_ratio(counts, "verbs")
        features.at[index, 'adverb_ratio'] = POS_ratio(counts, "adverbs")
        features.at[index, 'adjectives_ratio'] = POS_ratio(counts, "adjectives")
        features.at[index, 'others_ratio'] = POS_ratio(counts, "others")

    features = features.drop(['domain'], axis = 1)
    features = features.drop(['POS'], axis = 1)
    features = features.drop(['split_words'], axis = 1)
    return features
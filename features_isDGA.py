import re
import pandas as pd
import numpy as np
from collections import Counter

# A portion of this code was written by following worksheets found at https://github.com/yevheniyc/Projects in the DGA Detection using Machine Learning Series
# Part 1 - Feature Engineering: https://notebook.community/yevheniyc/Python/1m_ML_Security/notebooks/day_3/Worksheet%205%20-%20Feature%20Engineering

# Calculate Shannon Entropy for a word
def H_entropy (word):
    prob = [ float(word.count(c)) / len(word) for c in dict.fromkeys(list(word)) ] 
    H = - sum([ p * np.log2(p) for p in prob ]) 
    return H

# Calculate vowel to consonant ratio
def vowel_consonant_ratio (x):
    x = x.lower()
    vowels_pattern = re.compile('([aeiou])')
    consonants_pattern = re.compile('([b-df-hj-np-tv-z])')
    vowels = re.findall(vowels_pattern, x)
    consonants = re.findall(consonants_pattern, x)
    try:
        ratio = len(vowels) / len(consonants)
    except: # catch zero devision exception 
        ratio = 0  
    return ratio


# ngrams: Implementation according to Schiavoni 2014: "Phoenix: DGA-based Botnet Tracking and Intelligence"
# http://s2lab.isg.rhul.ac.uk/papers/files/dimva2014.pdf
def ngrams(word, n):
    # Extract all ngrams and return a regular Python list
    # Input word: can be a simple string or a list of strings
    # Input n: Can be one integer or a list of integers 
    # if you want to extract multipe ngrams and have them all in one list
    
    l_ngrams = []
    if isinstance(word, list):
        for w in word:
            if isinstance(n, list):
                for curr_n in n:
                    try:
                        ngrams = [w[i:i+curr_n] for i in range(0,len(w)-curr_n+1)]
                    except TypeError:
                        pass
                    l_ngrams.extend(ngrams)
            else:
                ngrams = [w[i:i+n] for i in range(0,len(w)-n+1)]
                l_ngrams.extend(ngrams)
    else:
        if isinstance(n, list):
            for curr_n in n:
                ngrams = [word[i:i+curr_n] for i in range(0,len(word)-curr_n+1)]
                l_ngrams.extend(ngrams)
        else:
            ngrams = [word[i:i+n] for i in range(0,len(word)-n+1)]
            l_ngrams.extend(ngrams)
#     print(l_ngrams)
    return l_ngrams

# ngrams: Implementation according to Schiavoni 2014: "Phoenix: DGA-based Botnet Tracking and Intelligence"
# http://s2lab.isg.rhul.ac.uk/papers/files/dimva2014.pdf
def ngram_feature(domain, d, n):
    # Input is your domain string or list of domain strings
    # a dictionary object d that contains the count for most common english words
    # finally you n either as int list or simple int defining the ngram length
    
    # Core magic: Looks up domain ngrams in english dictionary ngrams and sums up the 
    # respective english dictionary counts for the respective domain ngram
    # sum is normalized
    
    l_ngrams = ngrams(domain, n)
    count_sum=0
    for ngram in l_ngrams:
        if d[ngram]:
            count_sum+=d[ngram]
    try:
        feature = count_sum/(len(domain)-n+1)
    except:
        feature = 0
    return feature

#sum of ngrams features
def average_ngram_feature(l_ngram_feature):
    return sum(l_ngram_feature)/len(l_ngram_feature)

#get all the english ngrams from top 10000 words
def get_eng_ngrams():
    top_en_words = pd.read_csv("./data/google-10000-english.txt", header=None, names=['words'])
    l_en_ngrams = ngrams(list(top_en_words['words']), [1,2,3])
    ngrams_counter = Counter(l_en_ngrams)

    return ngrams_counter
    
#length of domain
def length(domain):
    return len(domain)

#number of digits in the domain
def digit_count(domain):
    return domain.count('[0.9]')


#extract features from either a singular domain, or a data_frame
def extract_features(ngrams_counter = get_eng_ngrams(), domain = "", data_frame = None):
    if data_frame is None:
        d = {'domain': [domain]}
        features = pd.DataFrame(data=d)
    else:
        features = data_frame
    features['length'] = features.domain.apply(length)
    features['digits'] = features.domain.apply(digit_count)
    features['entropy'] = features.domain.apply(H_entropy)
    features['vowel-cons'] = features.domain.apply(vowel_consonant_ratio)
    features['ngrams'] = features.domain.apply(lambda x : average_ngram_feature([ngram_feature(x, ngrams_counter, 1), ngram_feature(x, ngrams_counter, 2), ngram_feature(x, ngrams_counter, 3)]))

    features = features.drop(['domain'], axis = 1)
    return features
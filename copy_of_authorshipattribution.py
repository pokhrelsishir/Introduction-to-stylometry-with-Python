# -*- coding: utf-8 -*-
"""Copy of AuthorshipAttribution.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1u4e6F4hFaqlYS4Dc3HL-BD9856MLRFIn

# Loading in the Data
"""

from google.colab import drive
drive.mount('/content/drive')

papers = {
    'Madison': [10, 14, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48], # 14 known Madision papers
    'Hamilton': [1, 6, 7, 8, 9, 11, 12, 13, 15, 16, 17, 21, 22, 23, 24, # 51 known Hamilton papers
                 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 59, 60,
                 61, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 
                 78, 79, 80, 81, 82, 83, 84, 85],
    'Jay': [2, 3, 4, 5], # 4 of the 5 known Jay papers; 64 is the other known Jay paper
    'Shared': [18, 19, 20], # 3 co-written Madison/Hamilton papers claimed by Madison
    'Disputed': [49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 62, 63], # 12 disputed papers
    'TestCase': [64] # Jay's 5th paper, held as a test case
}

# A function that compiles all of the text files associated with a single author into a single string
def read_files_into_string(filenames):
    strings = []
    for filename in filenames:
        with open(f'/content/drive/My Drive/Google CREWE/data/federalist_{filename}.txt') as f:
            strings.append(f.read())
    return '\n'.join(strings)

# Make a dictionary out of the authors' corpora
federalist_by_author = {}  
for author, files in papers.items():
    federalist_by_author[author] = read_files_into_string(files)
 
# check that the files loaded properly
for author in papers:
    print(federalist_by_author[author][:100])

"""# First Stylometric Test: Mendenhall's Characteristic Curves of Composition"""

# Load nltk 
import nltk
# install nltk 'punkt'
nltk.download('punkt')

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline

# Compare the disputed papers to those written by everyone, 
# including the shared ones. 
authors = ("Hamilton", "Madison", "Disputed", "Jay", "Shared")

# Transform the authors' corpora into lists of word tokens
federalist_by_author_tokens = {}
federalist_by_author_length_distributions = {}
for author in authors:
    tokens = nltk.word_tokenize(federalist_by_author[author])
    
    # Filter out punctuation
    federalist_by_author_tokens[author] = ([token for token in tokens 
                                            if any(c.isalpha() for c in token)])
   
    # Get a distribution of token lengths
    token_lengths = [len(token) for token in federalist_by_author_tokens[author]]
    federalist_by_author_length_distributions[author] = nltk.FreqDist(token_lengths)
    federalist_by_author_length_distributions[author].plot(15,title=author)

"""# Second Stylometric Test: John Burrows' Delta Method"""

# Feature Selection

# Who are we dealing with this time?
authors = ("Hamilton", "Madison", "Jay", "Disputed", "Shared")

# Combine every paper except our test case into a single corpus
whole_corpus = []
for author in authors:
    whole_corpus += federalist_by_author_tokens[author]

# Get a frequency distribution
whole_corpus_freq_dist = list(nltk.FreqDist(whole_corpus).most_common(30)) # use the top 30 most frequent words as features
# Most of these 30 will be funtion words and common verbs. Remember that function words are a useful tool for stylometry. Their
# usage is not something that is consciously monitored by an individual and they are topic-independent
print(whole_corpus_freq_dist[ :10 ]) # Print a sample of the most frequent words

# Put the features in a list
features = []
for item in whole_corpus_freq_dist:
    features.append(item[0])
print(features)

import pprint
#Calculating features for each subcorpus

# The main data structure
feature_freqs = {}

for author in authors:
    # A dictionary for each candidate's features
    feature_freqs[author] = {} 
    
    # A helper value containing the number of tokens in the author's subcorpus
    overall = len(federalist_by_author_tokens[author])
    
    # Calculate each feature's presence in the subcorpus
    for feature in features:
        # Count the number of times each feature appears
        presence = federalist_by_author_tokens[author].count(feature)
        feature_freqs[author][feature] = presence / overall
        print(author, ",",feature, ":", presence, "/", overall, "=", feature_freqs[author][feature])
pprint.pprint(feature_freqs)

#Calculating feature averages and standard deviations

import math

# The data structure into which we will be storing the "corpus standard" statistics
corpus_features = {}

# For each feature...
for feature in features:
    # Create a sub-dictionary that will contain the feature's mean 
    # and standard deviation
    corpus_features[feature] = {}
    
    # Calculate the mean of the relative frequencies expressed in the subcorpora
    feature_average = 0
    for author in authors:
        feature_average += feature_freqs[author][feature] #adding together the relative frequency from all authors
    feature_average = feature_average/len(authors) # dividing the sum by the number of authors
    corpus_features[feature]["Mean"] = feature_average # entering the value in the dictionary
    
    # Calculate the standard deviation using the basic formula for a sample
    feature_stdev = 0
    for author in authors:
        diff = feature_freqs[author][feature] - corpus_features[feature]["Mean"] # subtract the standard deviation from the rel freq
        feature_stdev += diff*diff # square the difference
    feature_stdev = feature_stdev / (len(authors) - 1) # divide by the number of authors - 1
    feature_stdev = math.sqrt(feature_stdev) # take the square root
    corpus_features[feature]["StdDev"] = feature_stdev # add the value to the dictionary

pprint.pprint(corpus_features)

# Calculating z-scores
feature_zscores = {}
for author in authors:
    feature_zscores[author] = {}
    for feature in features:
        
        # Z-score definition = (value - mean) / stddev
        # We use intermediate variables to make the code easier to read
        feature_val = feature_freqs[author][feature]
        feature_mean = corpus_features[feature]["Mean"]
        feature_stdev = corpus_features[feature]["StdDev"]
        feature_zscores[author][feature] = ((feature_val-feature_mean) / 
                                            feature_stdev)

pprint.pprint(feature_zscores)

# Calculating features and z-scores for our test case
# Tokenize the test case
testcase_tokens = nltk.word_tokenize(federalist_by_author["TestCase"])

# Filter out punctuation and lowercase the tokens
testcase_tokens = [token for token in testcase_tokens 
                   if any(c.isalpha() for c in token)]
 
# Calculate the test case's features
overall = len(testcase_tokens)
testcase_freqs = {}
for feature in features:
    presence = testcase_tokens.count(feature)
    testcase_freqs[feature] = presence / overall # relative frequency in the testcase
    print(feature, ":", presence, "/", overall, "=", testcase_freqs[feature])
    
# Calculate the test case's feature z-scores
testcase_zscores = {}
for feature in features:
    feature_val = testcase_freqs[feature]
    feature_mean = corpus_features[feature]["Mean"]
    feature_stdev = corpus_features[feature]["StdDev"]
    testcase_zscores[feature] = (feature_val - feature_mean) / feature_stdev
    print("Test case z-score for feature", "'", feature,"'", "is", testcase_zscores[feature])

# Calculating Delta

for author in authors:
    delta = 0
    for feature in features:
         # take the absolute value of the difference between the z-scores of the feature in the test case and the feature in the 
         # author's subcorpus
        delta += math.fabs((testcase_zscores[feature] - 
                            feature_zscores[author][feature]))
    delta /= len(features) # divide the sum by the number of features to find the delta for that author
    print( "Delta score for candidate", author, "is", delta )
    
# Remember the smallest Delta is the predicted author

"""Activities adapted from: Laramée, François Dominic. (2018) "Introduction to stylometry with Python," The Programming Historian. Use under CC BY 4.0.
Access at: https://programminghistorian.org/en/lessons/introduction-to-stylometry-with-python
"""
from utilities import Sentence, loadUsefulTrainingData, loadTrainingData, tokenize
import json
import numpy as np 
from collections import defaultdict, Counter
import operator

#load reviews 
static_training_data_dir = 'static_training_data/'
training_set = loadTrainingData(static_training_data_dir)

for sent in training_set:
	sent.tokens= tokenize(sent.content) # tokenize all sentences 
	if sent.labeled_aspects == 'other features':
		sent.labeled_aspects = 'no feature'  # convert all other features to no feature

# compile all to dictionary of list
static_aspect_dic = defaultdict(list)
for sent in training_set:
	static_aspect_dic[sent.labeled_aspects] = static_aspect_dic[sent.labeled_aspects] + sent.tokens

sent_count_dic = dict.fromkeys(static_aspect_dic.keys(),0)
for sent in training_set:
	sent_count_dic[sent.labeled_aspects] = sent_count_dic[sent.labeled_aspects] + 1

# create a two keys dictionary
static_word_dict = {}
for static_keys in static_aspect_dic:
	word_freq_dic = Counter(static_aspect_dic[static_keys])
	for word_key in word_freq_dic:
		static_word_dict[(static_keys,word_key)]=word_freq_dic[word_key]

#Example: number of word in static class 'price' that has key word camera
print static_word_dict[('price','camera')]

#compute frequency of all words
all_word_list =[]
for static_keys in static_aspect_dic:
	all_word_list = all_word_list + static_aspect_dic[static_keys] # combine list
all_word_freq_dic = Counter(all_word_list)

# generate tf-idf frequency
nd = len(training_set)*1.0
idf_dict = dict.fromkeys(static_word_dict.keys(),[])
for tuple_keys in idf_dict:
	static_key = tuple_keys[0]
	key_word = tuple_keys[1]
	key_word_count = all_word_freq_dic[key_word]
	idf = np.log(nd/(1.0+key_word_count)) # this should potentially be change
	idf_dict[tuple_keys]= static_word_dict[tuple_keys]*idf/sent_count_dic[static_key]

# generate ordered list for each class
output_dict ={}
for static_keys in static_aspect_dic:
	d1 = {}
	for tuple_keys in idf_dict:
		if static_keys==tuple_keys[0]:
			d1[tuple_keys[1]] = idf_dict[tuple_keys]
	sorted_list = sorted(d1.items(), key=operator.itemgetter(1),reverse=True)[:10]
	#output_dict[static_keys] = [tup[0] for tup in sorted_list ]
	output_dict[static_keys]  = sorted_list

#prepare for output to txt file
save_wordlist_path= 'predictor_data/wordlist_dict_idf_value_snow.txt'
_file = open(save_wordlist_path, 'w')
json.dump(output_dict, _file)
_file.close()


# print output_dict

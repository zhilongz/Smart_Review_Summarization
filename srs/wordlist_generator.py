from utilities import Sentence, loadUsefulTrainingData, loadTrainingData, tokenize
import json
import numpy as np 
from collections import defaultdict, Counter
import operator

def merge_otherft(sentences_set):
	for sent in sentences_set:
		sent.tokens= tokenize(sent.content) # tokenize all sentences 
		if sent.labeled_aspects == 'other features':
			sent.labeled_aspects = 'no feature'  # convert all other features to no feature

def get_static_aspect(sentences_set):
	static_aspect_dic = defaultdict(list)
	for sent in sentences_set:
		static_aspect_dic[sent.labeled_aspects] = static_aspect_dic[sent.labeled_aspects] + sent.tokens	
	return static_aspect_dic

def get_num_sent_in_aspect(sentences_set):
	static_aspect_dic = get_static_aspect(sentences_set)
	sent_count_dic = dict.fromkeys(static_aspect_dic.keys(),0)
	for sent in sentences_set:
		sent_count_dic[sent.labeled_aspects] = sent_count_dic[sent.labeled_aspects] + 1
	return sent_count_dic

def get_word_freq(sentences_set):
	#compute frequency of all words and return a dictionary
	static_aspect_dic = get_static_aspect(sentences_set)
	all_word_list =[]
	for static_keys in static_aspect_dic:
		all_word_list = all_word_list + static_aspect_dic[static_keys] # combine list
	all_word_freq_dic = Counter(all_word_list)
	return all_word_freq_dic

def tf_idf(sentences_set,num_key_word):
	static_aspect_dic = get_static_aspect(sentences_set)
	all_word_freq_dic = get_word_freq(sentences_set)
	sent_count_dic = get_num_sent_in_aspect(sentences_set)

	# create a two keys dictionary
	static_word_dict = {}
	for static_keys in static_aspect_dic:
		word_freq_dic = Counter(static_aspect_dic[static_keys])
		for word_key in word_freq_dic:
			static_word_dict[(static_keys,word_key)]=word_freq_dic[word_key]
	
	# generate tf-idf frequency
	nd = len(sentences_set)*1.0
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
		sorted_list = sorted(d1.items(), key=operator.itemgetter(1),reverse=True)[:num_key_word]
		#output_dict[static_keys] = [tup[0] for tup in sorted_list ]
		output_dict[static_keys]  = sorted_list

	return output_dict

def save2doc(output_dict,save_wordlist_path):
	#prepare for output to txt file
	_file = open(save_wordlist_path, 'w')
	json.dump(output_dict, _file)
	_file.close()

def gen_wordlist(static_training_data_dir,save_wordlist_path,num_key_word):
	#load reviews 
	training_set = loadTrainingData(static_training_data_dir)
	#merge other feature as no feature 
	merge_otherft(training_set)
	output_dict = tf_idf(training_set,num_key_word)
	# save output_dict
	save2doc(output_dict,save_wordlist_path)

if __name__ == '__main__':
	static_training_data_dir = 'static_training_data/'
	save_wordlist_path = 'predictor_data/wordlist_dict_idf_value_snow.txt'
	# define number of key word to remain in the order tf-idf ranked list of words
	num_key_word = 10
	gen_wordlist(static_training_data_dir,save_wordlist_path,num_key_word)
		
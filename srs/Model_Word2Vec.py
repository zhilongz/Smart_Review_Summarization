import numpy as np
import math as math
import word2vec
from utilities import Sentence, Product, AspectPattern

class AspectPatterns(object):
	def __init__(self, pattern_name_list):
		#possible pattern_name: adj_nn, nn, adj, adv
		self.aspectPatterns_list = []
		for pattern_name in pattern_name_list:
			if pattern_name == 'adj_nn':
				aspectPatterns_1 = []
				pattern_structure ="""adj_nn:{<JJ><NN.?>}"""
				aspectTagIndices = [0,1]
				aspectPattern = AspectPattern(name='adj_nn', structure=pattern_structure, aspectTagIndices=aspectTagIndices)
				aspectPatterns_1.append(aspectPattern)

				pattern_structure ="""nn_nn:{<NN.?><NN.?>}"""
				aspectPattern = AspectPattern(name='nn_nn', structure=pattern_structure, aspectTagIndices=aspectTagIndices)
				aspectPatterns_1.append(aspectPattern)
				self.aspectPatterns_list.append(aspectPatterns_1)

			elif pattern_name == 'nn':
				aspectPatterns_2 = []
				pattern_structure ="""nn:{<NN.?>}"""
				aspectTagIndices = [0]
				aspectPattern = AspectPattern(name='nn', structure=pattern_structure, aspectTagIndices=aspectTagIndices)
				aspectPatterns_2.append(aspectPattern)
				self.aspectPatterns_list.append(aspectPatterns_2)

			elif pattern_name == 'adj':
				aspectPatterns_3 = []
				pattern_structure ="""adj:{<JJ.?>}"""
				aspectTagIndices = [0]
				aspectPattern = AspectPattern(name='adj', structure=pattern_structure, aspectTagIndices=aspectTagIndices)
				aspectPatterns_3.append(aspectPattern)
				self.aspectPatterns_list.append(aspectPatterns_3)

			elif pattern_name == 'adv':
				aspectPatterns_4 = []
				pattern_structure ="""adv_compara:{<RBR>}"""
				aspectTagIndices = [0]
				aspectPattern = AspectPattern(name='adv_compara', structure=pattern_structure, aspectTagIndices=aspectTagIndices)
				aspectPatterns_4.append(aspectPattern)

				pattern_structure ="""adv_super:{<RBS>}"""
				aspectTagIndices = [0]
				aspectPattern = AspectPattern(name='adv_super', structure=pattern_structure, aspectTagIndices=aspectTagIndices)
				aspectPatterns_4.append(aspectPattern)
				self.aspectPatterns_list.append(aspectPatterns_4)


def distill_dynamic(sentence, aspectPatterns):
	if not sentence.pos_tagged_tokens:
		sentence.pos_tag()
	sentence.word2vec_matchDaynamicAspectPatterns(aspectPatterns.aspectPatterns_list)

def distill_dynamic_sentencelist(sentence_list, aspectPatterns):
	for sentence in sentence_list:
		if not sentence.pos_tagged_tokens:
			sentence.pos_tag()
		sentence.word2vec_matchDaynamicAspectPatterns(aspectPatterns.aspectPatterns_list)


def static_aspect_to_vec(static_aspects_all, model):
	wordlist_dic = static_aspects_all['wordlist_dic']
	static_aspect_list_show = static_aspects_all['static_aspect_list_show']
	static_aspect_list_fortraining = static_aspects_all['static_aspect_list_fortraining']

	num_useful=len(static_aspect_list_fortraining)
	static_wordlist_vec=[[] for i in range(num_useful)]
	for i in range(num_useful):
		for j in range(len(wordlist_dic[static_aspect_list_show[i]])):
			word=wordlist_dic[static_aspect_list_show[i]][j]
			if word in model:
				static_wordlist_vec[i].append(model[word])

	return static_wordlist_vec


def predict_aspect_word2vec(sentence, model, aspectPatterns, static_aspect_list, static_wordlist_vec, criteria_for_choosing_class = "max", similarity_measure = "max", cp_threshold = 0.85, ratio_threshold = 0):
	# aspectPattern_namelist: 'adj_nn': all adj+nn and nn+nn; 'nn': all nn; adj: all adj; adv: all adv
	# criteria_for_choosing_class: choose from 'max', 'sum', 'sum_max'. See explanation below
	# similarity_measure:  choose from 'max', 'sum_row_max', 'max_column_mean','mean'. See explanation below
	# cp_threshold: the threshold for the top class's similarity, for a sentence to be classified as useful
	# ratio_threshold: the threshold for the ratio between top and second class's similarity, for a sentence to be classified as useful

	num_static_aspect=len(static_wordlist_vec)
	distill_dynamic(sentence, aspectPatterns) #distill the sentence's dynamic aspects

	#transform the sentence's word2vec_features to vectors
	word2vec_features = []
	for item in sentence.word2vec_features_list:
		word2vec_features=word2vec_features + item
	vec_list=[]
	if word2vec_features:
		for dynamic_aspect in word2vec_features:
			dynamic_aspect_splitted=dynamic_aspect.split(' ')
			aspect_phrase_vec=[]
			for aspect in dynamic_aspect_splitted:
				if aspect in model:
					aspect_word_vec=model[aspect]
					aspect_phrase_vec.append(aspect_word_vec)
			if aspect_phrase_vec:
				vec_list.append(aspect_phrase_vec)	
	
	#calculating vector distance of the dynamic aspects to each phrase in the static aspect:
	#similarity_matrix is the similarity matrix, and (i,j) entry is the similarity between the i th word in the dynamic aspect and the j th word in the static aspect.
	if vec_list:
		similarity_matrix=np.zeros([len(vec_list),num_static_aspect])
		for i in range(len(vec_list)):
			for j in range(num_static_aspect):			   
				similarity_item_matrix=np.zeros([len(vec_list[i]),len(static_wordlist_vec[j])])
				for kk in range(len(vec_list[i])):
					for ll in range(len(static_wordlist_vec[j])):
						similarity_item_matrix[kk][ll]=np.dot(vec_list[i][kk],static_wordlist_vec[j][ll])
				if similarity_measure == 'max':
					similarity_item=np.max(similarity_item_matrix)
				elif similarity_measure == 'sum_row_max':
					similarity_item_row=np.max(similarity_item_matrix,axis=1)
					similarity_item=np.sum(similarity_item_row)
				elif similarity_measure == 'max_column_mean':
					similarity_item_column=np.mean(similarity_item_matrix,axis=0)
					similarity_item=np.max(similarity_item_column)
				elif similarity_measure == 'mean':
					similarity_item=np.mean(similarity_item_matrix)
				similarity_matrix[i][j]=similarity_item

		# criteria_for_choosing_class: 'max': choose the class that has the highest max similarity with any of the dynamic aspects;   'sum': choose the class that has the highest sum similarity with dynamic aspect list;  'sum_max': for any dynamic aspect, only preserve its highest similarity class, and choose the class that has the highest sum
		similarity_catagory=[0 for j in range(num_static_aspect)]
		if criteria_for_choosing_class == 'max':
			for j in range(num_static_aspect):
				similarity_catagory[j]=np.max(similarity_matrix[:,j])
		if criteria_for_choosing_class == 'sum':
			for j in range(num_static_aspect):
				similarity_catagory[j]=np.sum(similarity_matrix[:,j])
		if criteria_for_choosing_class == 'sum_max':
			similarity_maxmatching_matrix=np.zeros([len(vec_list),num_static_aspect])
			for i in range(len(vec_list)):
				k=0
				max_k=0
				for j in range(num_static_aspect):
					if similarity_matrix[i,j]>max_k:
						k=j
						max_k=similarity_matrix[i,j]
				similarity_maxmatching_matrix[i,k]=max_k
			for j in range(num_static_aspect):
				similarity_catagory[j]=np.sum(similarity_maxmatching_matrix[:,j])

		# Sort the sentence's similarity to each class
		similarity_list_sorted,static_aspect_list_sorted = (list(x) for x in zip(*sorted(zip(similarity_catagory, static_aspect_list), reverse=True)))
		sim_whole_list_sorted=[]
		for i in range(num_static_aspect):
			item=(static_aspect_list_sorted[i],round(similarity_list_sorted[i],4))
			sim_whole_list_sorted.append(item)
		if sim_whole_list_sorted[0][1]>cp_threshold:
			if sim_whole_list_sorted[1][1]!=0 and sim_whole_list_sorted[0][1]/sim_whole_list_sorted[1][1]>=ratio_threshold:
				prediction=sim_whole_list_sorted[0][0]
			elif sim_whole_list_sorted[1][1]==0 and sim_whole_list_sorted[0][1]!=0:
				prediction=sim_whole_list_sorted[0][0]
			else: prediction='useless'
		else: prediction='useless'
		return (prediction,sim_whole_list_sorted)
	else:
		return ('useless',[])
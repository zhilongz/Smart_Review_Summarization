import os
import json
import sys
import numpy as np
import word2vec
from abc import ABCMeta, abstractmethod
from maxEntropyModel import cond_prob, loadWordListDict, train
from word2VecModel import AspectPatterns, predict_aspect_word2vec, static_aspect_to_vec, distill_dynamic, getCosineDistanceFeatureVector
from utilities import loadUsefulTrainingData, loadScraperDataFromDB, Sentence
from srs import settings
from sklearn.externals import joblib


def getPredictorDataFilePath(filename):
		
	predictor_datafile_path = os.path.join(settings["predictor_data"], filename)
	if os.path.exists(predictor_datafile_path):
		return predictor_datafile_path
	else:
		raise Exception("{} is not found!".format(predictor_datafile_path))

#defining abstract class Predictor
class Predictor(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	def load(self):
		pass

	@abstractmethod
	def train(self):
		pass

	@abstractmethod
	def predict(self, sentence):
		pass

	@abstractmethod
	def predict_for_sentences(self, sentences):
		pass


class MaxEntropy_Predictor(Predictor):
	"""
	A class to predict static aspects for given sentences using maxEntropyModel
	"""

	def __init__(self):

		self.params = [] # would be lambda_star from training results
		self.staticAspectList = []
		self.wordlist_dict = []

	def load(self, wordlist_filename, param_filename):
		self.loadParams(param_filename)
		self.loadWordListDict(wordlist_filename)

	def loadParams(self, param_filename):

		params_file_path = getPredictorDataFilePath(param_filename)
		file = open(params_file_path, 'r')
		params = np.array(json.load(file))
		file.close()
		self.params = params

	def loadWordListDict(self, wordlist_filename):
		wordlist_dict_path = getPredictorDataFilePath(wordlist_filename)
		self.wordlist_dict = loadWordListDict(wordlist_dict_path)
		self.staticAspectList = sorted(self.wordlist_dict.keys())

	def train(self, wordlist_filename, lamda_opt_filename):
		# load wordlist_dict and static_aspect_list
		self.loadWordListDict(wordlist_filename)
		
		# load training data
		static_training_data_dir = settings["static_training_data"]
		training_set = loadUsefulTrainingData(static_training_data_dir)

		lambda_len = len(self.wordlist_dict)*len(self.staticAspectList)
		res = train(self.wordlist_dict, self.staticAspectList, training_set[:500], lambda_len)

		self.params = res.x

		save_lamda_path = os.path.join(settings["predictor_data"],lamda_opt_filename)
		self.saveLambda(save_lamda_path)

	def saveLambda(self, save_lamda_path):
		# save optimized lambda into file
		lambda_file = open(save_lamda_path, 'w')
		json.dump(list(self.params), lambda_file)
		lambda_file.close()

	def predict(self, sentence, cp_threshold=0.5,debug=False):
		"""
		INPUT: `Sentence` object: sentence
		OUTPUT: `str` onject: predicted_aspect
		"""
		params = self.params
		static_aspect_list = self.staticAspectList
		wordlist_dict = self.wordlist_dict

		cp = cond_prob(params, wordlist_dict, static_aspect_list,sentence, isTraining=False)

		predicted_aspect_index = cp.index(max(cp)) 
		predicted_aspect = static_aspect_list[predicted_aspect_index]

		if max(cp) > cp_threshold:
			# predictor confidently knows what static aspect the 
			# sentence belongs to
			predicted_aspect_index = cp.index(max(cp)) 
			predicted_aspect = static_aspect_list[predicted_aspect_index]
		else:
			predicted_aspect = 'no feature'
		if debug:
			return predicted_aspect, max(cp)
		else:
			return predicted_aspect

	def predict_for_sentences(self, sentences, cp_threshold=0.5, debug=False):

		for sentence in sentences:
			if debug:
				sentence.static_aspect = self.predict(sentence, cp_threshold=cp_threshold, debug=debug)[0]
			else:
				sentence.static_aspect = self.predict(sentence, cp_threshold=cp_threshold)


class Word2Vec_Predictor(Predictor):
	def __init__(self, aspectPattern_names=['adj_nn','nn']):
		self.aspectPatterns = AspectPatterns(aspectPattern_names)
		self.model = []
		self.static_aspects_all = []
		self.static_seedwords_vec = []

	def load(self, model_filename, word2vec_dict_filename):
		model_file_path = getPredictorDataFilePath(model_filename)
		word2vec_dict_path = getPredictorDataFilePath(word2vec_dict_filename)
		self.model = word2vec.load(model_file_path)  #load word2vec model
		file = open(word2vec_dict_path, 'r')
		self.static_aspects_all = json.load(file)
		file.close()

		self.static_seedwords_vec = static_aspect_to_vec(self.static_aspects_all, self.model)

	def train(self):
		pass

	def predict(self, sentence, criteria_for_choosing_class = "max", similarity_measure = "max", cp_threshold = 0.85, ratio_threshold = 0):
		
		static_aspect_list = self.static_aspects_all["static_aspect_list"]
		

		prediction, class_scores = predict_aspect_word2vec(sentence, self.model, 
			self.aspectPatterns, static_aspect_list, static_seedwords_vec, 
			criteria_for_choosing_class, similarity_measure, cp_threshold, ratio_threshold)
		return prediction, class_scores


	def predict_for_sentences(self, sentences, criteria_for_choosing_class = "max", similarity_measure = "max", cp_threshold = 0.4, ratio_threshold = 0):
		
		predictions = []
		for sentence in sentences:
			sentence.static_aspect, _ = self.predict(sentence, criteria_for_choosing_class, 
				similarity_measure, cp_threshold, ratio_threshold)
			predictions.append(sentence.static_aspect)

		return np.array(predictions)

class Word2Vec_svm_Predictor(Predictor):
	def __init__(self, aspectPattern_names=['adj_nn','nn']):
		self.aspectPatterns = AspectPatterns(aspectPattern_names)
		self.model = []
		self.static_aspects_all = []
		self.svm = None
		self.static_seedwords_vec = []

	def load(self, model_filename, word2vec_dict_filename, svm_filename):
		model_file_path = getPredictorDataFilePath(model_filename)
		word2vec_dict_path = getPredictorDataFilePath(word2vec_dict_filename)
		svm_path = getPredictorDataFilePath(svm_filename)
		self.model = word2vec.load(model_file_path)  #load word2vec model
		file = open(word2vec_dict_path, 'r')
		self.static_aspects_all = json.load(file)
		file.close()

		self.svm = joblib.load(svm_path)
		self.static_seedwords_vec = static_aspect_to_vec(self.static_aspects_all, self.model) 

	def train(self):
		pass

	def predict(self, sentence):
		
		# transform sentence into a vec
		useful_features_vec = getCosineDistanceFeatureVector(sentence, 
			self.aspectPatterns, self.model, self.static_aspects_all, self.static_seedwords_vec)

		# use svm to map vec to a label
		prediction = self.svm.predict(useful_features_vec.reshape(1, -1))[0]

		return prediction


	def predict_for_sentences(self, sentences):
		
		predictions = []
		for sentence in sentences:
			sentence.static_aspect = self.predict(sentence)
			predictions.append(sentence.static_aspect)

		return np.array(predictions)



def loadTrainedPredictor(predictor_name):
	
	if predictor_name == 'MaxEntropy':
		params_filename = 'lambda_opt_regu3.txt'
		wordlist_filename = 'wordlist_dict_1.txt'
		predictor = MaxEntropy_Predictor()
		predictor.load(wordlist_filename, params_filename)
	elif predictor_name == 'Word2Vec':
		predictor = Word2Vec_Predictor()
		predictor.load('text8.bin','word2vec_dict.txt')

	elif predictor_name == 'Word2Vec_svm':
		predictor = Word2Vec_svm_Predictor()
		predictor.load('text8.bin','word2vec_dict.txt', 'w2v_svm/w2v_svm.pkl')
	return predictor


if __name__ == '__main__':
	# main()
	# create test sentences
	static_traning_data_dir = settings["static_training_data"]

	# sentences = loadTrainingData(static_traning_data_dir)
	sentences = loadUsefulTrainingData(static_traning_data_dir)

	# testing for Word2Vec predictor
	p = loadTrainedPredictor('Word2Vec_svm')	
	
	for sentence in sentences:
		print sentence.content
		print p.predict(sentence)

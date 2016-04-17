import os
import json
import sys
import numpy as np
from maxEntropyModel import cond_prob, loadWordListDict, train
from utilities import loadUsefulTrainingData

class StaticPredictor(object):
	"""
	A class to predict static aspects for given sentences using
	maxEntropyModel
	"""

	def __init__(self):

		self.params = [] # would be lambda_star from training results
		self.staticAspectList = []
		self.wordlist_dict = []

	def loadParams(self, param_file):
		file = open(param_file, 'r')
		params = np.array(json.load(file))
		file.close()
		self.params = params

	def loadWordListDict(self, wordlist_dict_path):
		self.wordlist_dict = loadWordListDict(wordlist_dict_path)
		self.staticAspectList = sorted(self.wordlist_dict.keys())

	def train(self, wordlist_dict_path, static_training_data_dir, save_lamda_path):
		# load wordlist_dict and static_aspect_list
		self.loadWordListDict(wordlist_dict_path)
		
		# load training data
		training_set = loadUsefulTrainingData(static_training_data_dir)

		lambda_len = len(self.wordlist_dict)*len(self.staticAspectList)
		res = train(self.wordlist_dict, self.staticAspectList, training_set[:500], lambda_len)

		self.params = res.x
		self.saveLambda(save_lamda_path)

	def saveLambda(self, save_lamda_path):
		# save optimized lambda into file
		lambda_file = open(save_lamda_path, 'w')
		json.dump(list(self.params), lambda_file)
		lambda_file.close()

	def predict(self, sentence, cp_threshold=0.0,debug=False):
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

def main():
	staticPredictor = StaticPredictor()

	wordlist_dict_path = 'predictor_data/wordlist_dict_1.txt'
	static_training_data_dir = 'static_training_data/'
	save_lamda_path = 'predictor_data/lambda_opt.txt'

	staticPredictor.train(wordlist_dict_path, static_training_data_dir, save_lamda_path)

if __name__ == '__main__':
	main()
		

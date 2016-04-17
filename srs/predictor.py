import os
import json
import sys
import numpy as np
from maxEntropyModel import cond_prob, loadWordListDict, train, loadUsefulTrainingData

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

	def loadStaticAspectList(self, static_aspect_list_file):
		file = open(static_aspect_list_file, 'r')
		static_aspect_list = json.load(file)
		file.close()
		self.staticAspectList = sorted(static_aspect_list)


	def train(self):
		self.wordlist_dict = loadWordListDict('predictor_data/wordlist_dict_dict.txt')
		print self.wordlist_dict
		self.loadStaticAspectList('predictor_data/static_aspect_list.txt')
		print self.staticAspectList
		static_traning_data_dir = os.path.abspath('static_training_data/')
		training_set = loadUsefulTrainingData(static_traning_data_dir)

		print "training sentences: {0}".format(len(training_set))

		lambda_len = len(self.wordlist_dict)*len(self.staticAspectList)
		res = train(self.wordlist_dict, self.staticAspectList, training_set[:500], lambda_len)

		self.params = res.x
		self.saveLambda()

	def saveLambda(self):
		# save optimized lambda into file
		lambda_file = open('predictor_data/lambda_opt.txt', 'w')
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
	staticPredictor.train()
	# staticPredictor.loadParams('predictor_data/lambda_opt.txt')
	# staticPredictor.loadStaticAspectList('predictor_data/static_aspect_list.txt')
	# for i in range(11):
	# 	print staticPredictor.staticAspectList[i], staticPredictor.params[i*11:(i+1)*11]



if __name__ == '__main__':
	main()
		

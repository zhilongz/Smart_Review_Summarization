
from predictor import *
from utilities import Sentence, loadUsefulTrainingData, loadTrainingData
from maxEntropyModel import loadWordListDict
import os
import json
import unittest
from srs import settings

class TestMaxEntropy_Predictor(unittest.TestCase):

	def setUp(self):
		"""
		A method that is run before each unit test in this class.
		"""
		self.staticPredictor = MaxEntropy_Predictor()
		param_filename = 'lambda_opt_regu3.txt'
		wordlist_filename = 'wordlist_dict_1.txt'
		self.staticPredictor.loadParams(param_filename)
		self.staticPredictor.loadWordListDict(wordlist_filename)

	def testPredictForOneSentence(self):
		# create test sentences
		content = "It produces great photo!"
		sentence = Sentence(content=content)

		# accuracy
		predicted_aspect = self.staticPredictor.predict(sentence)
		print predicted_aspect
	
	def testPredictForSentences(self):
		# create test sentences
		static_traning_data_dir = settings["static_training_data"]

		# sentences = loadTrainingData(static_traning_data_dir)
		sentences = loadUsefulTrainingData(static_traning_data_dir)
		# accuracy
		correct = 0.0
		correct_idx = []
		for idx, sentence in enumerate(sentences):
			predicted_aspect = self.staticPredictor.predict(sentence)
			if predicted_aspect == sentence.labeled_aspects:
				correct += 1
				correct_idx.append(idx)
		class_error = 1.0 - correct/len(sentences)
		print 'The classification error is: %.2f' % (class_error)

if __name__ == '__main__':
    unittest.main()
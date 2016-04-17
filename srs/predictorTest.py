
from predictor import StaticPredictor
from utilities import Sentence, loadUsefulTrainingData, loadTrainingData
from maxEntropyModel import loadWordListDict
import os
import unittest

class TestStaticPredictor(unittest.TestCase):

	def setUp(self):
		"""
		A method that is run before each unit test in this class.
		"""
		self.staticPredictor = StaticPredictor()
		params_path = 'predictor_data/lambda_opt_1.txt'
		wordlist_dict_path = 'predictor_data/wordlist_dict_1.txt'
		self.staticPredictor.loadParams(params_path)
		self.staticPredictor.loadWordListDict(wordlist_dict_path)

	def testPredictForOneSentence(self):
		# create test sentences
		content = "It produces great photo!"
		sentence = Sentence(content=content)

		# accuracy
		predicted_aspect = self.staticPredictor.predict(sentence)
		print predicted_aspect
	
	def testPredictForSentences(self):
		# create test sentences
		static_traning_data_dir = os.path.abspath('static_training_data/')

		# sentences = loadTrainingData(static_traning_data_dir)
		sentences = loadUsefulTrainingData(static_traning_data_dir)
		# accuracy
		correct = 0.0
		for sentence in sentences:
			predicted_aspect = self.staticPredictor.predict(sentence)
			if predicted_aspect == sentence.labeled_aspects:
				correct += 1
		class_error = 1.0 - correct/len(sentences)
		print 'The classification error is: %.2f' % (class_error)

if __name__ == '__main__':
    unittest.main()
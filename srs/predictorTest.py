
from predictor import StaticPredictor
from utilities import Sentence
from maxEntropyModel import load_labelled_sent
import os
import unittest

class TestStaticPredictor(unittest.TestCase):

	def setUp(self):
		"""
		A method that is run before each unit test in this class.
		"""
		self.staticPredictor = StaticPredictor()
		params_file = 'predictor_data/lambda_opt.txt'
		static_aspect_list_file = 'predictor_data/static_aspect_list.txt'
		self.staticPredictor.loadParams(params_file)
		self.staticPredictor.loadStaticAspectList(static_aspect_list_file)

	def testPredictForOneSentence(self):
		# create test sentences
		content = ".It's small size enough to be easily held in one hand, and is so light as to be barely  noticeable when carried in a small padded bag hung around the neck."
		sentence = Sentence(content=content)

		# accuracy
		predicted_aspect = self.staticPredictor.predict(sentence)
		print predicted_aspect
	
	def testPredictForSentences(self):
		# create test sentences
		static_traning_data_dir = os.path.abspath('static_training_data/')

		sentences = []
		for data_file in os.listdir(static_traning_data_dir):
		    if data_file.endswith('labeled.txt'):
		        sentences.extend(load_labelled_sent(os.path.join(static_traning_data_dir, data_file)))

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
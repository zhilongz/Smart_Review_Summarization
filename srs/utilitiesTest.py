from utilities import *
import unittest

class TestUtilities(unittest.TestCase):

	def setUp(self):
		"""
		A method that is run before each unit test in this class.
		"""
		product_name = 'Nokia'
		reviewTrainingFile = product_name + '.txt'
		self.product = Product(name=product_name)
		self.product.loadReviewsFromTrainingFile('data/trainingFiles/' + reviewTrainingFile)
		

	def testLoadReviewsFromTrainingFile(self):
		assert len(self.product.reviews) == 41
		assert len(self.product.reviews[0].sentences) == 10

	def testPosTag(self):
		review0 = self.product.reviews[0]
		for sentence in review0.sentences:
			sentence.pos_tag()

if __name__ == '__main__':
    unittest.main()
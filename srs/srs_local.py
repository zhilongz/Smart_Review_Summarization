from scraper import main as scraper_main, createAmazonScraper
from predictor import MaxEntropy_Predictor, Word2Vec_Predictor, loadTrainedPredictor
from srs import settings
from utilities import loadScraperDataFromDB, Sentence
from swnModel import get_sentiment_score_for_sentences, get_ftScore_ftSenIdx_dicts
from sentiment_plot import box_plot
from database import upsert_contents_for_product_id, update_for_product_id
import os

def get_ft_dicts_from_contents(contents, predictor):
	sentences = []
	for cont in contents:
		sentences.append(Sentence(content=cont))

	
	predictor.predict_for_sentences(sentences)	#if Maxentropy, the cp_threshold=0.5, if Word2Vec, the cp_threshold should be 0.85 for criteria_for_choosing_class = "max", similarity_measure = "max"
	get_sentiment_score_for_sentences(sentences)
	return get_ftScore_ftSenIdx_dicts(sentences)
	

def fill_in_db(amazonScraper, product_id, predictor_name = 'MaxEntropy'):
	
	# fetch product info from db 
	prod1_contents, prod1_ft_score_dict, prod1_ft_senIdx_dict = loadScraperDataFromDB(product_id)

	if len(prod1_contents) == 0: # not in db yet
		# scrape contents
		prod1_contents = scraper_main(amazonScraper, product_id)
		
		# classify, sentiment score
		predictor = loadTrainedPredictor(predictor_name)
		prod1_ft_score_dict, prod1_ft_senIdx_dict = \
		get_ft_dicts_from_contents(prod1_contents, predictor)
		
		# insert new entry
		upsert_contents_for_product_id(product_id, prod1_contents, \
			prod1_ft_score_dict, prod1_ft_senIdx_dict)

		return True
	
	elif len(prod1_ft_score_dict) == 0 or len(prod1_ft_senIdx_dict) == 0:
		
		# classify, sentiment score
		predictor = loadTrainedPredictor(predictor_name)
		prod1_ft_score_dict, prod1_ft_senIdx_dict = \
		get_ft_dicts_from_contents(prod1_contents, predictor)
		
		# update old entry
		update_for_product_id(product_id, prod1_ft_score_dict, prod1_ft_senIdx_dict)

		return True
	else:
		print "Filled in db before for {0}".format(product_id)

		return False
	
def plot(product_id):
	_, prod1_ft_score_dict, _ = loadScraperDataFromDB(product_id)
	plot_folder = settings['sentiment_plot']
	figure_file_path = os.path.join(plot_folder, product_id + '_boxplot.png')
	box_plot(prod1_ft_score_dict, figure_file_path, product_id)

def main(product_id):
	a = createAmazonScraper()
	fill_in_db(a, product_id)
	plot(product_id)

if __name__ == '__main__':
	product_id = 'B00HZE2PYI'
	main(product_id)
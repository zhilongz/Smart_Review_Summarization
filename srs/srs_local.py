from scraper import main as scraper_main, createAmazonScraper,scrape_reviews_hard
from predictor import StaticPredictor, loadTrainedStaticPredictor
from srs import settings
from utilities import loadScraperDataFromDB, Sentence
from swnModel import get_sentiment_score_for_sentences, get_ftScore_ftSenIdx_dicts
from sentiment_plot import box_plot
from database import upsert_contents_for_product_id, update_for_product_id
import os

def get_ft_dicts_from_contents(contents, staticPredictor):
	sentences = []
	for cont in contents:
		sentences.append(Sentence(content=cont))

	staticPredictor.predict_for_sentences(sentences)	
	get_sentiment_score_for_sentences(sentences)
	return get_ftScore_ftSenIdx_dicts(sentences)
	

def fill_in_db(product_id):
	
	# fetch product info from db 
	prod1_contents, prod1_ft_score_dict, prod1_ft_senIdx_dict = loadScraperDataFromDB(product_id)

	if len(prod1_contents) == 0: # not in db yet
		# scrape contents
		try: 
			amazonScraper = createAmazonScraper()
			prod1_contents = scraper_main(amazonScraper, product_id)
		except: 
			prod1_contents = scrape_reviews_hard(product_id)
			print 'Amazon API failed. Scrape the hard way!'

		# classify, sentiment score
		staticPredictor = loadTrainedStaticPredictor()
		prod1_ft_score_dict, prod1_ft_senIdx_dict = \
		get_ft_dicts_from_contents(prod1_contents, staticPredictor)
		
		# insert new entry
		upsert_contents_for_product_id(product_id, prod1_contents, \
			prod1_ft_score_dict, prod1_ft_senIdx_dict)

		return True
	
	elif len(prod1_ft_score_dict) == 0 or len(prod1_ft_senIdx_dict) == 0:
		
		# classify, sentiment score
		staticPredictor = loadTrainedStaticPredictor()
		prod1_ft_score_dict, prod1_ft_senIdx_dict = \
		get_ft_dicts_from_contents(prod1_contents, staticPredictor)
		
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
	fill_in_db(product_id)
	plot(product_id)

if __name__ == '__main__':
	product_id = 'B00HV6KL6Y'
	main(product_id)
from scraper import main as scraper_main, createAmazonScraper, scrape_number_review
from predictor import StaticPredictor, loadTrainedStaticPredictor
from srs import settings
from utilities import loadScraperDataFromDB, Sentence
from swnModel import get_sentiment_score_for_sentences, get_ftScore_ftSenIdx_dicts
from sentiment_plot import box_plot
from database import upsert_contents_for_product_id, update_for_product_id, update_contents_for_product_id, select_for_product_id
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
	prod_contents, prod_ft_score_dict, prod_ft_senIdx_dict = loadScraperDataFromDB(product_id)

	if len(prod_contents) == 0: # not in db yet
		# scrape contents
		amazonScraper = createAmazonScraper()
		prod_contents, prod_review_ids, prod_ratings, prod_num_reviews = scraper_main(amazonScraper, product_id)
			
		# classify, sentiment score
		staticPredictor = loadTrainedStaticPredictor()
		prod_ft_score_dict, prod_ft_senIdx_dict = \
		get_ft_dicts_from_contents(prod_contents, staticPredictor)
		
		# insert new entry
		upsert_contents_for_product_id(product_id, prod_contents, \
			prod_review_ids, prod_ratings, prod_num_reviews, \
			prod_ft_score_dict, prod_ft_senIdx_dict)

		return True
	
	elif len(prod_ft_score_dict) == 0 or len(prod_ft_senIdx_dict) == 0:
		'''
		this only triggered if product review is loaded from file and not scraped directly
		'''
		# classify, sentiment score
		staticPredictor = loadTrainedStaticPredictor()
		prod_ft_score_dict, prod_ft_senIdx_dict = \
		get_ft_dicts_from_contents(prod_contents, staticPredictor)
		
		# update old entry
		update_for_product_id(product_id, prod_ft_score_dict, prod_ft_senIdx_dict)

		return True

	else:
		print "Filled in db before for {0}".format(product_id)
		# scrape for current number of review 
		num_review_current = scrape_number_review(product_id)
		# query for number of reviews stored in db 
		query_res = select_for_product_id(product_id)
		num_review_db = len(query_res[0]["review_ids"])

		if num_review_current > num_review_db and num_review_db < 30: 
			print "But not enough review in db, scrapping for more..."
			# scrape contents
			amazonScraper = createAmazonScraper()
			prod_contents, prod_review_ids, prod_ratings, prod_num_reviews = scraper_main(amazonScraper, product_id,True)

			# classify, sentiment score
			staticPredictor = loadTrainedStaticPredictor()
			prod_ft_score_dict, prod_ft_senIdx_dict = \
			get_ft_dicts_from_contents(prod_contents, staticPredictor)
			
			# append new entry to existing entry
			update_contents_for_product_id(product_id, prod_contents, \
				prod_review_ids, prod_ratings, prod_num_reviews, \
				prod_ft_score_dict, prod_ft_senIdx_dict)

			return True
		else: 
			# didn't do anything to db
			print "There is enough review in db for analysis"
			return False
	
def plot(product_id):
	_, prod_ft_score_dict, _ = loadScraperDataFromDB(product_id)
	plot_folder = settings['sentiment_plot']
	figure_file_path = os.path.join(plot_folder, product_id + '_boxplot.png')
	box_plot(prod_ft_score_dict, figure_file_path, product_id)

def main(product_id):
	fill_in_db(product_id)
	plot(product_id)

if __name__ == '__main__':
	product_id = 'B00T85PH2Y'
	fill_in_db(product_id)
	# complete review in db: B00HZE2PYI,B00HV6KL6Y,B010RANXS8,B00T85PH2Y
	# partial review in db: B00MBPO5A8
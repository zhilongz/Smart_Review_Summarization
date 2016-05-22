from scraper import main as scraper_main
from swnModel import swnModel
from srs import settings
import os

def main(prod1ID, prod2ID, scrapeFlag=True):
	
	# scrap data
	if scrapeFlag:
		scraper_main(prod1ID)
		if prod2ID != None:
			scraper_main(prod2ID)

	# prepare static predictor params  
	params_filename = 'lambda_opt_regu2.txt'
	wordlist_filename = 'wordlist_dict_1.txt'
	
	# sentiment analysis and plot
	plot_folder = settings['sentiment_plot']
	if prod2ID == None:
		figure_file_path = os.path.join(plot_folder, prod1ID + '_boxplot.png')
		swnModel(params_filename,wordlist_filename,figure_file_path,prod1ID)
	else:
		figure_file_path = plot_folder + prod1ID + '_'+ prod2ID + '_boxcompare.png'
		swnModel(params_filename,wordlist_filename,figure_file_path,prod1ID,prod2ID)

if __name__ == '__main__':
	prod1ID = 'B00I8BICB2'
	prod2ID = 'B00HZE2PYI'
	scrapeFlag = False
	main(prod1ID, prod2ID, scrapeFlag)
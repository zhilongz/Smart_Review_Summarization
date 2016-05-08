from scraper import main as scraper_main
from swnModel import swnModel


def main():
	prod1ID = 'B00I8BICB2'
	prod2ID = 'B00HZE2PYI'
	scrapFlag = False
	
	# scrap data
	if scrapFlag:
		scraper_main(prod1ID)
		scraper_main(prod2ID)

	# prepare static predictor params  
	params_file = 'predictor_data/lambda_opt_regu2.txt'
	wordlist_dict_path = 'predictor_data/wordlist_dict_1.txt'
	
	# sentiment analysis and plot
	plot_folder = "sentiment_plot/"
	figure_filename = plot_folder + prod1ID + '_boxplot.png'
	swnModel(params_file,wordlist_dict_path,figure_filename,prod1ID)

	figure_filename = plot_folder + prod1ID + '_'+ prod2ID + '_boxcompare.png'
	swnModel(params_file,wordlist_dict_path,figure_filename,prod1ID,prod2ID)


if __name__ == '__main__':
	main()
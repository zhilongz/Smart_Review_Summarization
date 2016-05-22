import os 

def getPath(folder):
	parent_dir = os.path.dirname(os.path.realpath(__file__))
	return os.path.join(parent_dir, folder)

settings = {
"predictor_data": getPath("predictor_data"),
"scraper_data": getPath("scraper_data"),
"static_training_data": getPath("static_training_data"),
"sentiment_plot": getPath("sentiment_plot"),
}
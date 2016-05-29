from math import pi
import pandas as pd
from bokeh.plotting import figure, show, output_file
import numpy as np

def sentimentBoxPlot(feature_scorelist_dict):

	features = []
	mids = []
	spans = []

	for feature, scorelist in feature_scorelist_dict.items():
		features.append(feature)
		scorearray = np.array(scorelist)
		mean = np.mean(scorearray)
		span = np.percentile(scorearray, 75) - np.percentile(scorearray, 25)

		mids.append(mean)
		spans.append(span)

	TOOLS = "resize,save"
	p = figure(tools=TOOLS, plot_width=720, plot_height=480, x_range=features)
	w = 0.2
	p.rect(features, mids, w, spans, fill_color="#F2583E", line_color="black")
	
	p.title = "Product Review Aspect Summary"
	p.xaxis.major_label_orientation = pi/4
	p.grid.grid_line_alpha=0.3
	return p


from math import pi
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, TapTool, CustomJS, HoverTool
import numpy as np
from matplotlib import pyplot as plt

def prepareDataForRectPlot(feature_scorelist_dict, sort=True, spanTop=75, spanBottom=25):
	"""
	INPUT: feature_scorelist_dict
	OUTPUT: mids, spans
	"""

	features = feature_scorelist_dict.keys()
	if sort:
		features = sorted(features)
	
	mids = []
	spans = []
	for feature in features:
		scorelist = feature_scorelist_dict[feature]
		scorearray = np.array(scorelist)
		mean = np.mean(scorearray)
		span = np.percentile(scorearray, spanTop) - np.percentile(scorearray, spanBottom)

		mids.append(mean)
		spans.append(span)

	return mids, spans

def prepareDataForHistPlotAndSampleSentences(
	feature_scorelist_dict, feature_senIdxlist_dict, contents, sort=True, exampleSentences_size=3):
	"""
	INPUT: feature_scorelist_dict, feature_senIdxlist_dict, contents
	OUTPUT: histTops, histLefts, histRights, sampleSentences_dict
	"""

	features = feature_scorelist_dict.keys()
	if sort:
		features = sorted(features)

	histTops = []
	histLefts = []
	histRights = []
	sampleSentences_dict = {}
	for feature in features:
		# get raw data: scorelist
		scorelist = feature_scorelist_dict[feature]
		senIdxlist = feature_senIdxlist_dict[feature]

		score_num = len(scorelist)
		min_score = min(scorelist)
		max_score = max(scorelist)
		
		# determine bin_num
		bin_num = 4
		if score_num <= 10: bin_num = 2
		elif score_num <= 30: bin_num = 3
		elif score_num <= 100: bin_num = 4
		else: bin_num = 5

		# initialize histTop
		histTop = [0 for _ in range(bin_num)]
		exampleSentences = [[] for _ in range(bin_num)]

		delimiter = np.linspace(min_score, max_score, bin_num+1)
		
		for senIdx, score in zip(senIdxlist, scorelist):
			for j in range(bin_num):
				if score >= delimiter[j] and score <= delimiter[j+1]:
					histTop[j] += 1
					if len(exampleSentences[j]) < exampleSentences_size:
						content = contents[senIdx]
						exampleSentences[j].append(content)

					break
		histLeft = list(delimiter[0:bin_num])
		histRight = list(delimiter[1:bin_num+1])
		
		histTops.append(histTop)
		histLefts.append(histLeft)
		histRights.append(histRight)
		sampleSentences_dict[feature] = exampleSentences

	hist_cds = ColumnDataSource(data=dict(tops=histTops, lefts=histLefts, rights=histRights, features=features))
	sampleSentences_cds = ColumnDataSource(data=sampleSentences_dict)

	return hist_cds, sampleSentences_cds

def getRectPlot(features, mids, spans, w=0.3, fill_color="#2ca25f", hover_color="#99d8c9",
	plot_width=650, plot_height=450, major_label_orientation=pi/4, 
	grid_line_alpha=0.3, axis_label_text_font_size='12pt'):

	# plot rectPlot
	rectPlot = figure(tools="", plot_width=plot_width, plot_height=plot_height, x_range=features,y_axis_label="Sentiment Score")
	rectPlot.yaxis.axis_label_text_font_size = axis_label_text_font_size
	rectPlot.xaxis.axis_label_text_font_size = axis_label_text_font_size
	rectPlot.xaxis.major_label_orientation = major_label_orientation
	rectPlot.grid.grid_line_alpha=grid_line_alpha
	rectPlot.logo = None
	rectPlot.toolbar_location = None

	rectPlot_rect=rectPlot.rect(features, mids, w, spans, fill_color=fill_color, line_color=fill_color,hover_color=hover_color, hover_alpha=1.0)

	return rectPlot, rectPlot_rect

def getHistPlot(histPlot_cds, color="#99d8c9",
	grid_line_alpha=0.3, axis_label_text_font_size='12pt'):

	histPlot = figure(tools="", plot_width=400, plot_height=250,y_axis_label='Comments',x_axis_label="Sentiment Score")
	histPlot.xaxis.axis_label_text_font_size = axis_label_text_font_size
	histPlot.yaxis.axis_label_text_font_size = axis_label_text_font_size
	histPlot.logo = None
	histPlot.toolbar_location = None

	# initialize plot
	histPlot_quad = histPlot.quad(top='top',bottom='bottom',left='left',right='right', source=histPlot_cds,line_width=2,fill_alpha=0.8,color=color)

	return histPlot, histPlot_quad

def getInitialHistPlotData(hist_cds):

	top = hist_cds.data["tops"][0]
	left = hist_cds.data["lefts"][0]
	right = hist_cds.data["rights"][0]
	bottom = [0 for _ in top]
	feature = hist_cds.data["features"][0]
	histPlot_data = dict(top=top, bottom=bottom, left=left, right=right, feature=feature)
	histPlot_cds=ColumnDataSource(data=histPlot_data)

	return histPlot_cds

def sentimentBoxPlot(contents, feature_scorelist_dict, feature_senIdxlist_dict):

	# get data for rectPlot
	features = sorted(feature_scorelist_dict.keys())
	mids, spans = prepareDataForRectPlot(feature_scorelist_dict, sort=True)

	# get data for histPlot and sample reviews
	hist_cds, sampleSentences_cds = prepareDataForHistPlotAndSampleSentences(
	feature_scorelist_dict, feature_senIdxlist_dict, contents, sort=True)

	# plot rectPlot
	rectPlot, rectPlot_rect = getRectPlot(features, mids, spans)

	# plot histPlot
	histPlot_cds = getInitialHistPlotData(hist_cds)
	histPlot, histPlot_quad = getHistPlot(histPlot_cds)

	# add interaction between rectPlot and histPlot
	hoverJS="""
		var histPlot_data = histPlot_cds.get('data');
		var features = hist_cds.get('data')['features'];
		var hist_data = hist_cds.get('data');

		//get current hovering index
		fillHistData(cb_data, histPlot_data, features, hist_data);		
		histPlot_cds.trigger('change');
        
		"""

	hoverCallBack=CustomJS(args={'histPlot_cds':histPlot_cds, 'hist_cds':hist_cds},code=hoverJS)
	rectPlot.add_tools(HoverTool(renderers=[rectPlot_rect],callback=hoverCallBack,tooltips=None))

	# add interaction between histPlot and sample reviews
	hoverJS2="""
		var sampleSentences_dict = sampleSentences_cds.get('data');
		
		var feature = histPlot_cds.get('data')['feature'];
		fillSampleReviews(cb_data, sampleSentences_dict, feature);
        
		""" 

	hoverCallBack2=CustomJS(args={'sampleSentences_cds':sampleSentences_cds, 'histPlot_cds': histPlot_cds}, code=hoverJS2)
	histPlot.add_tools(HoverTool(renderers=[histPlot_quad],callback=hoverCallBack2,tooltips=None))

	return (rectPlot,histPlot)

def sentimentBoxPlot_Compare(feature_scorelist_dict,feature_scorelist_dict2):

	features = []
	mids = []
	spans = []
	all_score_list = []
	color_list = []
	color1 = "#F2583E"
	color2 = "#205fDf"
	color_hover = "olive"

	#Combining the two dictionaries into one list:
	for feature, scorelist in feature_scorelist_dict.items():
		if feature in feature_scorelist_dict2:			
			scorelist2 = feature_scorelist_dict2[feature]	
			feature2 = feature
			features = features + [feature,feature2]
			color_list = color_list +[color1, color2]

			scorearray = np.array(scorelist)
			mean = np.mean(scorearray)
			span = np.percentile(scorearray, 75) - np.percentile(scorearray, 25)
			scorearray2 = np.array(scorelist2)
			mean2 = np.mean(scorearray2)
			span2 = np.percentile(scorearray2, 75) - np.percentile(scorearray2, 25)

			mids = mids + [mean, mean2]
			spans = spans + [span, span2]
			all_score_list.append(scorelist)
			all_score_list.append(scorelist2)


	TOOLS = "save"
	p = figure(tools=TOOLS, plot_width=700, plot_height=470, x_range=features, title_text_font_size='16pt',y_axis_label="Sentiment Score")
	p.yaxis.axis_label_text_font_size = "12pt"
	p.xaxis.axis_label_text_font_size = "12pt"
	w = 0.3
	p_rect=p.rect(features, mids, w, spans, color = color_list, line_color="black",hover_color=color_hover, hover_alpha=1.0)
	
	p.title = "Product Review Aspect Summary"
	p.xaxis.major_label_orientation = pi/4
	p.grid.grid_line_alpha=0.3
	p.logo = None
	p.rect(legend = "Product 1", color = color1)
	p.rect(legend = "Product 2", color = color2)

	p2 = figure(tools="save,tap", title="Aspect Histogram", plot_width=400, plot_height=270,title_text_font_size='16pt',y_axis_label='# of sentences',x_axis_label="Sentiment Score")
	s2=ColumnDataSource(data=dict(top=[], bottom=[], left=[], right=[]))
	p2.quad(top='top',bottom='bottom',left='left',right='right', source=s2,line_width=2,fill_alpha=0.8,color=color_hover)
	p2.xaxis.axis_label_text_font_size = "12pt"
	p2.yaxis.axis_label_text_font_size = "12pt"
	p2.logo = None

	Hover_jscode="""
		var score_list = %s
		//var rect_data=Rects.get('data');

		//getting the source data for Fig.2
		var fig2data = s2.get('data');

		//get current hovering index
		var current_index = cb_data.index['1d'].indices[0];

		//defining linspace function
		var linspace = function linspace(a,b,n) {
		    if(typeof n === "undefined") n = Math.max(Math.round(b-a)+1,1);
		    if(n<2) { return n===1?[a]:[]; }
		    var i,ret = Array(n);
		    n--;
		    for(i=n;i>=0;i--) { ret[i] = (i*b+(n-i)*a)/n; }
		    return ret;
		}

		if (typeof current_index != 'undefined'){

			//Making histogram
			var selected_list=score_list[current_index];
			var min = Math.min(...selected_list);
			var max = Math.max(...selected_list);
			var score_num = selected_list.length;
			var bin_num = 4;
			if(score_num<=10){ bin_num = 2;} 
			else if (10 < score_num && score_num <= 30) { bin_num = 3;}
			else if (30 <score_num && score_num <= 100) { bin_num = 4;}
			else if (score_num > 100){bin_num = 5;
			}
			var hist = new Array(bin_num).fill(0);
			var delimiter = linspace (min, max, bin_num+1);
			for (i = 0; i < score_num; i++){
				score = selected_list[i];
				for (j = 0; j < bin_num; j++){
					if(delimiter[j] <= score && score < delimiter[j+1]){
						hist[j]++;
					}
				}
			}

			//Defining the drawing parameters for Fig2
			fig2data['bottom'] = new Array(bin_num).fill(0);
			fig2data['top'] = hist;
			fig2data['left']= delimiter.slice(0,bin_num);
			fig2data['right']= delimiter.slice(1,bin_num+1)


			console.log(fig2data);
	        s2.trigger('change');
		}
        
		""" % all_score_list
	Hover_CallBack=CustomJS(args={'s2':s2,'Rects':p_rect.data_source},code=Hover_jscode)
	p.add_tools(HoverTool(renderers=[p_rect],callback=Hover_CallBack,tooltips=None))
	return (p,p2)

# function for setting the colors of the box plots pairs
def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color,alpha=0)
    plt.setp(bp['caps'], color=color,alpha=0)
    plt.setp(bp['medians'], color=color,alpha=0)

def box_plot(prod1score,filename,prod1ID):
    ticks = prod1score.keys()
    
    prod1score_list = []
    for ft in ticks:
        prod1score_list.append(prod1score[ft])

    plt.figure(figsize=(7, 7))

    bpl = plt.boxplot(prod1score_list, positions=np.array(xrange(len(ticks)))*2.0, sym='', widths=0.6)
    set_box_color(bpl, '#D7191C') # colors are from http://colorbrewer2.org/

    plt.plot([], c='#D7191C', label=prod1ID)
    plt.legend()

    locs, labels = plt.xticks(xrange(0, len(ticks) * 2, 2), ticks)
    plt.xlim(-2, len(ticks)*2)
    plt.setp(labels, rotation=90)
    plt.axhline(y=0.0,xmin=0,xmax=3,c="blue",linewidth=0.5,zorder=0)
    plt.tight_layout()
    plt.savefig(filename)

def box_plot_compare(prod1score,prod2score,filename,prod1ID,prod2ID):
    ticks = prod1score.keys()
    
    prod1score_list = []
    for ft in ticks:
        prod1score_list.append(prod1score[ft])

    prod2score_list = []
    for ft in ticks:
        prod2score_list.append(prod2score[ft])

    plt.figure(figsize=(7, 7))

    bpl = plt.boxplot(prod1score_list, positions=np.array(xrange(len(ticks)))*2.0-0.4, sym='', widths=0.6)
    bpr = plt.boxplot(prod2score_list, positions=np.array(xrange(len(ticks)))*2.0+0.4, sym='', widths=0.6)
    set_box_color(bpl, '#D7191C') # colors are from http://colorbrewer2.org/
    set_box_color(bpr, '#2C7BB6')

    plt.plot([], c='#D7191C', label=prod1ID)
    plt.plot([], c='#2C7BB6', label=prod2ID)
    plt.legend()

    locs, labels = plt.xticks(xrange(0, len(ticks) * 2, 2), ticks)
    plt.xlim(-2, len(ticks)*2)
    plt.setp(labels, rotation=90)
    # plt.ylim(-0.5, 0.5)
    plt.axhline(y=0.0,xmin=0,xmax=3,c="blue",linewidth=0.5,zorder=0)
    plt.tight_layout()
    plt.savefig(filename)


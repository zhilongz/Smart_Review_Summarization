from math import pi
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, TapTool, CustomJS, HoverTool
import numpy as np
from matplotlib import pyplot as plt

def sentimentBoxPlot(contents, feature_scorelist_dict, feature_senIdxlist_dict):

	features = []
	mids = []
	spans = []
	all_score_list = []
	color1 = "#F2583E"
	color_hover = "olive"

	features = sorted(feature_scorelist_dict.keys())

	for feature in features:
		scorelist = feature_scorelist_dict[feature]
		scorearray = np.array(scorelist)
		mean = np.mean(scorearray)
		span = np.percentile(scorearray, 75) - np.percentile(scorearray, 25)

		mids.append(mean)
		spans.append(span)
		all_score_list.append(scorelist)

	TOOLS = "save"
	p = figure(tools=TOOLS, plot_width=700, plot_height=470, x_range=features, title_text_font_size='16pt',y_axis_label="Sentiment Score")
	p.yaxis.axis_label_text_font_size = "12pt"
	p.xaxis.axis_label_text_font_size = "12pt"
	w = 0.3
	p_rect=p.rect(features, mids, w, spans, fill_color=color1, line_color="black",hover_color=color_hover, hover_alpha=1.0)
	
	p.title = "Product Review Aspect Summary"
	p.xaxis.major_label_orientation = pi/4
	p.grid.grid_line_alpha=0.3
	p.logo = None

	p2 = figure(tools="save", title="Aspect Histogram", plot_width=400, plot_height=270,title_text_font_size='16pt',y_axis_label='# of sentences',x_axis_label="Sentiment Score")
	s2=ColumnDataSource(data=dict(top=[], bottom=[], left=[], right=[], feature=''))
	p2_quad = p2.quad(top='top',bottom='bottom',left='left',right='right', source=s2,line_width=2,fill_alpha=0.8,color=color_hover)
	p2.xaxis.axis_label_text_font_size = "12pt"
	p2.yaxis.axis_label_text_font_size = "12pt"
	p2.logo = None

	Hover_jscode="""
		//get score list data
		var all_score_list = all_score_list_data.get('data')['all_score_list'];

		//get the source data for Fig.2
		var fig2data = s2.get('data');
		var features = features_data.get('data')['features'];

		//get current hovering index
		fillHistData(cb_data, fig2data, features, all_score_list);		
		s2.trigger('change');
        
		"""

	all_score_list_data = ColumnDataSource(data=dict(all_score_list=all_score_list))
	features_data = ColumnDataSource(data=dict(features=features))

	Hover_CallBack=CustomJS(args={'s2':s2, 'features_data':features_data, 'all_score_list_data':all_score_list_data},code=Hover_jscode)
	p.add_tools(HoverTool(renderers=[p_rect],callback=Hover_CallBack,tooltips=None))

	# get sentences for each bin of histogram
	feature_example_sen_dict = {}
	for feature, scorelist in feature_scorelist_dict.items():

		score_num = len(scorelist)
		min_score = min(scorelist)
		max_score = max(scorelist)
		
		bin_num = 4
		if score_num <= 10: bin_num = 2
		elif score_num <= 30: bin_num = 3
		elif score_num <= 100: bin_num = 4
		else: bin_num = 5

		feature_example_sen_dict[feature] = {}
		for bin0 in range(bin_num):
			feature_example_sen_dict[feature][bin0] = []

		delimiter = np.linspace(min_score, max_score, bin_num+1)
		for i, score in enumerate(scorelist):

			senIdx = feature_senIdxlist_dict[feature][i]
			content = contents[senIdx]

			for j in range(bin_num):
				if score >= delimiter[j] and score <= delimiter[j+1]:
					example_sen = feature_example_sen_dict[feature][j]
					if len(example_sen) < 3:
						example_sen.append(content)
					else:
						continue
					break


	s3 = ColumnDataSource(data=feature_example_sen_dict)

	Hover_jscode2="""
		var feature_example_sen_dict = s3.get('data');
		var feature = s2.get('data')['feature'];
		var barIdx = cb_data.index['1d'].indices[0];

		if (typeof barIdx != 'undefined'){
		var example_sen = feature_example_sen_dict[feature][barIdx];
		console.log(example_sen[0]);
		document.getElementsByClassName("sample_reviews")[0].innerHTML = "Sample reviews:" + example_sen[0];
		}
		else {
		document.getElementsByClassName("sample_reviews")[0].innerHTML = "Sample reviews:";
		}
        
		""" 

	Hover_CallBack2=CustomJS(args={'s3':s3, 's2': s2}, code=Hover_jscode2)
	p2.add_tools(HoverTool(renderers=[p2_quad],callback=Hover_CallBack2,tooltips=None))

	return (p,p2)

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


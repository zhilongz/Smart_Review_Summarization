from math import pi
import pandas as pd
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource,OpenURL, TapTool,Select,CustomJS,HoverTool
import numpy as np
from matplotlib import pyplot as plt

def sentimentBoxPlot(feature_scorelist_dict):

	features = []
	mids = []
	spans = []
	all_score_list = []

	for feature, scorelist in feature_scorelist_dict.items():
		features.append(feature)
		scorearray = np.array(scorelist)
		mean = np.mean(scorearray)
		span = np.percentile(scorearray, 75) - np.percentile(scorearray, 25)

		mids.append(mean)
		spans.append(span)
		all_score_list.append(scorearray)

	TOOLS = "resize,save"
	p = figure(tools=TOOLS, plot_width=700, plot_height=460, x_range=features)
	w = 0.2
	p_rect=p.rect(features, mids, w, spans, fill_color="#F2583E", line_color="black",hover_color='olive', hover_alpha=1.0)
	
	p.title = "Product Review Aspect Summary"
	p.xaxis.major_label_orientation = pi/4
	p.grid.grid_line_alpha=0.3

	p2 = figure(tools="tap", title="line", plot_width=300, plot_height=300)
	s2=ColumnDataSource(data=dict(x=[], y=[]))
	p2.line('x', 'y', source=s2,line_width=2)

	jscode="""
		var data = s2.get('data');
		var rect_data=Rects.get('data');
		var current_data = cb_data;
		window.alert(rect_data.x);
        data['x']=[3,5,7];
        data['y']=[5,1,8];
        s2.trigger('change');
		"""
	CallBack=CustomJS(args={'s2':s2,'Rects':p_rect.data_source},code=jscode)
	p.add_tools(TapTool(callback=CallBack, renderers=[p_rect]))
	p.add_tools(HoverTool(renderers=[p_rect]))
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


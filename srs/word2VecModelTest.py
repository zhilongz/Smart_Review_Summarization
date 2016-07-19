import numpy as np
import math as math
import word2vec
from predictor import loadTrainedPredictor, Word2Vec_Predictor
from word2VecModel import distill_dynamic_sentencelist, AspectPatterns, static_aspect_to_vec
from utilities import Sentence

def Word2Vec_Predictor_test(sentence_list, aspectPattern_names, criteria_for_choosing_class, similarity_measure, cp_threshold, ratio_threshold, lookup, Isprint=0):
	# load Word2Vec predictor and initilize
	p = loadTrainedPredictor('Word2Vec')
	model = p.model
	aspectPatterns = AspectPatterns(aspectPattern_names)
	static_aspect_list = p.static_aspects_all["static_aspect_list"]
	static_wordlist_vec = static_aspect_to_vec(p.static_aspects_all, model)
	static_aspect_list_show = p.static_aspects_all['static_aspect_list_show']
	static_aspect_list_fortraining = p.static_aspects_all['static_aspect_list_fortraining']
	num_useful = len(static_aspect_list_fortraining)
	static_aspect_list_lookup={static_aspect_list[i]:i for i in range(num_useful)}
	for i in range(num_useful,len(static_aspect_list)):
		static_aspect_list_lookup[static_aspect_list[i]]=num_useful
	static_aspect_list_lookup['useless']=num_useful

	# Initilize classification matrix 
	classification_list=[]
	num_useful=len(static_aspect_list_fortraining)
	count=0
	count_correct=0
	count_useless_true=0
	count_useless_prediction=0
	count_useful_correct=0
	correctness_matrix=np.zeros([num_useful+1,num_useful+1],dtype=np.int)
	classified_sentences_true=[[] for i in range(num_useful+1)]
	classified_sentences_predict=[[] for i in range(num_useful+1)]
	classified_sentences_matrix=[[[] for j in range(num_useful+1)] for i in range(num_useful+1)]

	# Classify each sentence
	predictions = []
	for sentence in sentence_list:
		count=count+1
		aspect_prediction =p.predict(sentence, criteria_for_choosing_class, similarity_measure, cp_threshold, ratio_threshold)

		predictions.append(aspect_prediction[0])
		
		aspect_true=sentence.labeled_aspects
		classification=(aspect_true,aspect_prediction[0],sentence.word2vec_features_list,aspect_prediction[1][:3],sentence.content)

		#print classification
		classification_list.append(classification)
		correctness_matrix[static_aspect_list_lookup[aspect_true],static_aspect_list_lookup[aspect_prediction[0]]]+=1
		classified_sentences_true[static_aspect_list_lookup[aspect_true]].append(classification)
		classified_sentences_predict[static_aspect_list_lookup[aspect_prediction[0]]].append(classification)
		classified_sentences_matrix[static_aspect_list_lookup[aspect_true]][static_aspect_list_lookup[aspect_prediction[0]]].append(classification)

	count_useful_total=sum(sum(correctness_matrix[:num_useful,:]))
	count_useful_prediction_total=sum(sum(correctness_matrix[:,:num_useful]))
	count_useful_correct=sum(correctness_matrix.diagonal()[0:num_useful])
	count_correct=sum(correctness_matrix.diagonal())
	count_useless2useful=sum(sum(correctness_matrix[num_useful:num_useful+1,0:num_useful]))
	count_useful2useless=sum(sum(correctness_matrix[0:num_useful,num_useful:num_useful+1]))
	count_item_prediction=np.sum(correctness_matrix,axis=0)
	count_item_truelabel=np.sum(correctness_matrix,axis=1)
	correct_all=round(1.*count_correct/count,3)
	if abs(count_useful_prediction_total)>0.01:
		correct_useful_precision=round(1.*count_useful_correct/count_useful_prediction_total,3)
	else: correct_useful_precision=-1
	correct_useful_recall=round(1.*count_useful_correct/count_useful_total,3)
	if Isprint==1:
		correct_item_precision=np.zeros(num_useful+1)
		for ii in range(num_useful+1):
			if abs(count_item_prediction[ii])>0.01:
				correct_item_precision[ii]=np.divide(1.*correctness_matrix.diagonal()[ii],count_item_prediction[ii])
			else: correct_item_precision[ii]=-1
		correct_item_recall=np.divide(1.*correctness_matrix.diagonal(),count_item_truelabel)	
		print ((count,str(round(100.*correct_all,2))+'%'),(count_useful_total,str(round(100.*correct_useful_precision))+'%',str(round(100.*correct_useful_recall))+'%'),count_useless2useful,count_useful2useless)
		print static_aspect_list_show
		print correctness_matrix
		for i in range(len(classified_sentences_matrix[lookup[0]][lookup[1]])):
			print classified_sentences_matrix[lookup[0]][lookup[1]][i]
			print " "
	return np.array(predictions)

def load_labeled_file_without_aspect(file_name): 
    with open(file_name) as f:
        sentence_list =[]
        for line in f.readlines():
            line_splitted = line.split('***')
            if len(line_splitted)==2:
                sentence_list.append(Sentence(content=line_splitted[1],labeled_aspects=line_splitted[0]))
    return sentence_list

def load_labeled_file_with_aspect(file_name): 
	with open(file_name) as f:
		sentence_list =[]
		for line in f.readlines():
			line_splitted = line.split('***')
			if len(line_splitted) == 2:
				line_splitted_2 = line_splitted[1].split('####')
				word2vec_features_list=[]
				if len(line_splitted_2) == 2:
					all_feature_patterns=line_splitted_2[1][:-1]
					all_feature_patterns_split=all_feature_patterns.split('###')
					for feature_pattern in all_feature_patterns_split:
						word2vec_feature=[]
						feature_split=feature_pattern.split('##')
						for feature in feature_split:
							word2vec_feature.append(feature)	  
						word2vec_features_list.append(word2vec_feature)
					sentence_list.append(Sentence(content=line_splitted_2[0],labeled_aspects=line_splitted[0],word2vec_features_list=word2vec_features_list))
				elif len(line_splitted_2)==1:
					sentence_list.append(Sentence(content=line_splitted_2[0],labeled_aspects=line_splitted[0]))
	return sentence_list


def savetofile(sentence_list,filename):
	f=open(filename,'w+')
	for i in range(len(sentence_list)):
		if sentence_list[i].content[-1]=='\n':
			sentence=sentence_list[i].content[:-1]
		else: sentence=sentence_list[i].content

		if sentence_list[i].word2vec_features_list:
			features_string='#'
			for word2vec_features in sentence_list[i].word2vec_features_list:
				if word2vec_features:
					features_string+='#'
					for aspect in word2vec_features:
						features_string+='##'+aspect
				else: features_string+='### '
			f.write(sentence_list[i].labeled_aspects+"***"+sentence+features_string+'\n')
		else:
			f.write(sentence_list[i].labeled_aspects+"***"+sentence+'\n')
	f.close()

# transform a txt file without distilled aspects to one with distilled aspect, to save time for future use
def save_aspectPatterns_for_file(filename, new_filename):
	sentence_list = load_labeled_file_without_aspect(filename)
	aspectPatterns_list=AspectPatterns(['adj_nn','nn','adj','adv'])
	distill_dynamic_sentencelist(sentence_list, aspectPatterns_list)
	savetofile(sentence_list, new_filename)
	

if __name__ == '__main__':

	train_list = load_labeled_file_with_aspect('static_training_data/training_all_nn.txt')
	test_list = load_labeled_file_with_aspect('static_training_data/testing_all_nn.txt')

	#testing the precision and recall of the Word2Vec prediction
	test_result = Word2Vec_Predictor_test(train_list, aspectPattern_names = ['adj_nn','adj'], criteria_for_choosing_class = 'max', similarity_measure = 'max', cp_threshold = 0.85, ratio_threshold = 0, lookup = [1,1], Isprint=1)



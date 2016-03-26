# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 10:46:46 2016

@author: zhilong21
"""

#import math
import numpy as np
from scipy.optimize import minimize 
from nltk.tokenize import sent_tokenize, word_tokenize
import re
import csv

#load a list of features words extracted and acts as the dynamic aspect. The length of this list will determine the size of the model
dynamic_word_list = ['zoom','pictures','lens','quality','battery','price','digital','time','cameras','picture','image','shots','shoot','megapixel']

def f_vec(static_feat, ls): 
    """
    static_feat: a specfic static feature
    ls: a single labelled sentence obj 
    returns a vector of length len(dynamic_word_list)
    """
    global dynamic_word_list    
    #dynamic_word_list = ['zoom','pictures','lens','quality','battery','price','digital','time','cameras','picture','image','shots','shoot']
    
    #process sentence to a list of word without punctuation and number
    word_list = word_tokenize(ls.sent)
    punctuation = re.compile(r'[-.?!,":;()|0-9]') # remove these punctuations and number 
    word_list = [punctuation.sub("", word) for word in word_list]  
    word_list = filter(None, word_list) #filters empty         
    len_word = max(len(word_list),1)*1.0;
    f_value = []
    
    for w in dynamic_word_list: 
        if static_feat == ls.feat:
            f_value.append(word_list.count(w)/len_word)
        else: 
            return np.zeros(len(dynamic_word_list)) 
    return f_value
        
def cond_prob(lam_vec,feat_list,ls): 
    """ 
    lam_vec: lambda as a vector  
    feat_list: list of all static features 
    ls: a single labeled sentence obj 
        
    returns the conditional probability for all class (a vector)
    """
    cp = []
    for feat in feat_list: 
        f = f_vec(feat,ls) # a vector 
        numerator = np.exp(np.inner(lam_vec,f))
        deno = 0
        for c in feat_list:
            f = f_vec(c,ls) # a vector 
            deno = deno + np.exp(np.inner(lam_vec,f))
        cp.append(numerator/deno)
    return cp 

def loss_func(lam_vec,feat_list,ls_list):
    """ 
    loss function
    First argument is parameter vector to be optimized  
    """ 
    loss = 0
    for ls in ls_list: 
        f_cor = f_vec(ls.feat,ls) # a vector 
        deno = 0
        for c in feat_list:
            f = f_vec(c,ls) # a vector 
            deno = deno + np.exp(np.inner(lam_vec,f))
        
        loss_sent = np.inner(lam_vec,f_cor) - np.log(deno)
        loss = loss + loss_sent

    print loss    
    return loss*(-1)

def train(feat_list,ls_list,lambda_len):
    """ optimization by minimizing the loss function returns lambda* """
    lambda_guess = np.random.rand(lambda_len)*0.1
    res = minimize(loss_func, lambda_guess, args=(feat_list,ls_list), method='BFGS', options={'gtol': 1e-3, 'disp': True})
    return res
    """
    see for list of method: http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.optimize.minimize.html
    """
class labeled_sent:
    def __init__(self, feat, sent):
        self.feat = feat
        self.sent = sent

def load_labelled_sent(file_name): 
    with open(file_name) as f:
        c = csv.reader(f, delimiter='*')
        ls_list =[]
        for line in c:
            ls_list.append(labeled_sent(line[0],line[3]))
    return ls_list 

def main():
    # load a list of features words extracted and acts as the dynamic aspect. The length of this list will determine the size of the model
    # dynamic_word_list = ['zoom','pictures','lens','quality','battery','price','digital','time','cameras','picture','image','shots','shoot']
    
    # load a list of classes (static aspect)
    feat_list = ['price','pictures','video','zoom','size','design','battery','screen','detection','ease of use','quality','other features','no feature']
    
    # load labeled sentences as a list of labeled_sent
    ls_list = load_labelled_sent('B00B7O2Z42_labeled.txt')
    
    # train 
    n = len(dynamic_word_list)
    res = train(feat_list,ls_list[:180],n)
    
    lambda_star = res.x 
    print 'The lambda is: \n'
    print lambda_star
    
    #load unlabeled testing data (TBD) 
    #uls_list = load_labelled_sent('B00B7O2Z42_labeled.txt') 
    uls_list = ls_list[180:]    
    
    #validation 
    correct = 0.0
    for uls in uls_list:
        cp = cond_prob(lambda_star,feat_list,uls)
        predicted_class_index = cp.index(max(cp)) 
        if feat_list[predicted_class_index] == uls.feat:
            correct += 1
    
    class_error = 1.0 - correct/len(uls_list)
    print 'The classification error is: %.2f' % (class_error)

def testcase():
    # load a list of classes (static aspect)
    feat_list = ['price','pictures','video','zoom','size','design','battery','screen','detection','ease of use','quality','other features','no feature']
    
    # load labeled sentences as a list of labeled_sent
    ls_list = load_labelled_sent('B00B7O2Z42_labeled.txt')
    print f_vec(feat_list[1], ls_list[1])
    print feat_list[1]
    print len(ls_list)

    
if __name__ == "__main__":
    
    main() 
    #testcase()
    
    

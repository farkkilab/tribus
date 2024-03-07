import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture as GMM

def appr_fun(x, xroot, slope):
    ## heuristic for axxproimating the decision boundary
    y = np.exp( (x - xroot) * slope)
    y = y / (1.0 + y)
    return np.squeeze(y)

def compute_paras(mk_model, mk):
    ## compute the critical point of the decision bounary
    ## critical point is defined by P(theta = 1|x) = P(theta = 0|x) 
    ## given a 1-D two-mixture model
    ##
    ## inputs:
    ## mk_model: precomputed 2-gassian mixture model for all markers
    ## mk: one selected marker
    ##
    ## outputs:
    ## xroot: location of the critical point
    ## slope: slope of the decision boundary at the critical point
    
    mus, sigmas, ws = mk_model[mk]
    a = (-0.5 / sigmas[0] + 0.5 /sigmas[1])
    b = mus[0] / sigmas[0] - mus[1] / sigmas[1]
    c = 0.5 * (-mus[0] **2 / sigmas[0] + mus[1] ** 2 / sigmas[1]) + np.log(ws[0] / ws[1]) + 0.5 * np.log(sigmas[1] / sigmas[0])
    xroot = (-b - np.sqrt(b ** 2 - 4.0 * a * c) ) / (2.0 * a)
    slope = 0.5 * (xroot - mus[0]) / sigmas[0] - 0.5 * (xroot - mus[1]) / sigmas[1]
    return xroot, slope

def score_fun(x, mk_model, mk):
    ## compute the score function
    ## the score should roughly proportional to P(theta = + | x)

    xroot, slope = compute_paras(mk_model, mk)
    return appr_fun(x, xroot, slope)

def get_score_mat_main(X, table, mk_model):
    ## compute the cluster x annotation score matrix
    ## X: sample x feature data matrix
    ## table: a list of (ind, sign)
    score = np.zeros((X.shape[0], len(table.axes[1])))
    for i, ct in enumerate(table.columns):
        #score_tmp = np.zeros(X.shape[0])
        #count = 0.0
        score_tmp = np.ones(X.shape[0])
        count = 1.0
        for j, mk in enumerate(table.index):
            if table.loc[mk, ct] > 0:
                score_tmp =  np.min([score_tmp, score_fun(X[:, j], mk_model, mk)], axis = 0)
                #score_tmp +=  score_fun(X[:, j], mk_model, mk)
                #count += 1.0
            elif  table.loc[mk, ct] < 0:
                score_tmp =  np.min([score_tmp, 1.0 - score_fun(X[:, j], mk_model, mk)], axis = 0)
                #score_tmp +=  1.0 - score_fun(X[:, j], mk_model, mk)
                #count += 1.0
        score[:, i]= score_tmp / count
    return score

def compute_marker_model(df, table, thres):
    ## compute 2-gaussian mixture model for each marker
    ## output mean, variance, and weight for each marker
    mk_model = {}
    for mk in table.axes[0]:
        gmm = GMM(n_components=2, n_init=50, init_params="random_from_data")
        tmp = df[mk].to_numpy()
        gmm.fit(tmp[tmp > thres, np.newaxis])
        index = np.argsort(gmm.means_, axis = 0)    
        mk_model[mk] = (gmm.means_[index], gmm.covariances_[index], gmm.weights_[index])
        
    return mk_model
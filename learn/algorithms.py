# os-related imports
import sys
import csv

# numpy
import numpy as np

# algorithms
from sklearn import ensemble, svm, tree, linear_model

# statistics, metrics, x-fold val, plots
from sklearn.metrics import roc_curve, auc, confusion_matrix
from sklearn.cross_validation import StratifiedKFold
from sklearn.pipeline import Pipeline

from scipy import interp

def SVM(X, y, transformers):
    clf = svm.SVC(verbose=True, shrinking=False, probability=True, cache_size=1500, class_weight='auto')
    e_clf = ensemble.BaggingClassifier(clf, n_estimators=1, max_samples = 0.2, n_jobs=-1, verbose=True)
    results, _ = execute(X, y, transformers, lambda: e_clf)
    return results

def CART(X, y, transformers, out_file, field_names):
    results, model = execute(X, y, transformers, lambda: tree.DecisionTreeClassifier(max_depth=5, min_samples_leaf=50))
    if model:
        tree.export_graphviz(model, out_file=out_file, feature_names=field_names)
    return results

def RF(X, y, transformers):
    results, model =  execute(X, y, transformers, lambda: ensemble.RandomForestClassifier(n_estimators=100,max_depth=5, min_samples_leaf=50, n_jobs=-1))
    if model:
        features = model.feature_importances_
    else:
        features = False
    return results, features
   
def LR(X, y, transformers):
    results, model =  execute(X, y, transformers, lambda: linear_model.LogisticRegression())
    if model:
        features = model.coef_
    else:
        features = False
    return results, features

def execute(X, y, transformers, classifier):
    X = X.astype(np.float64)
    y = y.astype(np.float64)
    cv = StratifiedKFold(y, n_folds=5) # x-validation
    classifier = classifier()

    clf = Pipeline(transformers + [('classifier',classifier)])

    mean_tpr = 0.0
    mean_fpr = np.linspace(0, 1, 100)
    all_tpr = []
    cm=np.zeros((2,2))
    # cross fold validation
    for i, (train, test) in enumerate(cv):
        if sum(y[train]) < 5:
            print '...cannot train; too few positive examples'
            return False, False

        # train
        trained_classifier = clf.fit(X[train], y[train])

        # test
        y_pred = trained_classifier.predict_proba(X[test])

        # make cutoff for confusion matrix
        y_pred_binary = (y_pred[:,1] > 0.01).astype(int)

        # derive ROC/AUC/confusion matrix
        fpr, tpr, thresholds = roc_curve(y[test], y_pred[:, 1])
        mean_tpr += interp(mean_fpr, fpr, tpr)
        mean_tpr[0] = 0.0
        cm = cm + confusion_matrix(y[test], y_pred_binary) 

    mean_tpr /= len(cv)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    mean_cm = cm/len(cv)

    # redo with all data to return the features of the final model
    complete_classifier = clf.fit(X,y)

    return [mean_fpr, mean_tpr, mean_auc, mean_cm], complete_classifier.named_steps['classifier']

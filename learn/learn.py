import numpy as np
import matplotlib.pyplot as plt
import sys, os, csv
from itertools import product
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import SelectFpr
from sklearn.feature_selection import SelectPercentile
from sklearn.feature_selection import f_classif
from sklearn.feature_selection import chi2
import cx_Oracle

sys.path.append("src/")
import machine_learning as ml 
import in_out

def run_experiments(cursor, results_dir, algorithms=None):
	record_id = 'patientnummer'
	target_id = 'crc'
	c = (cursor, record_id, target_id, HIS, filtr, get_temporal_equivalent(merge))

	for alg in algorithms:
		if verbose: print "   ...with algorithm " + alg + " on 18-49 age interval"
		run_and_group_by_algorithm(c, alg, tbls18plus, results_dir+dir18plus+alg+'/', transformers, verbose)
		if verbose: print "   ...with algorithm " + alg + " on 30+ age interval"
		run_and_group_by_algorithm(c, alg, tbls30plus, results_dir+dir30plus+alg+'/', transformers, verbose)
		if verbose: print "   ...with algorithm " + alg + " on 50+ age interval"
		run_and_group_by_algorithm(c, alg, tbls50plus, results_dir+dir50plus+alg+'/', transformers, verbose)

	print 'Success!'

def run_and_group_by_algorithm(c, alg, files, out_dir, transformers, verbose, cutoff=0.005):
	if not files:
		return

	make_dirs(out_dir)

	results_list = []	
	for f in files:
		fname = f.split('/')[-1]
		fname = create_name(f.lower(), c[4])
		# get data, split in features/target
		if verbose: print "      ...for ", fname

		execute_query_with_tbl(c[0],f, c[3], c[4])
		X, y, headers = in_out.cursor2array(c) # assumption: first column is patientnumber and is pruned, last is target
	
		# run algorithm
		if alg == 'CART':
			results = ml.CART(X,y,transformers, out_dir+"/{}.dot".format(fname), headers,cutoff)
		elif alg == 'CART_entropy':
			results = ml.CART_entropy(X,y,transformers, out_dir+"/{}.dot".format(fname), headers, cutoff)
		elif alg == 'RF':
			results, features = ml.RandomForest(X, y,transformers, cutoff)
		elif alg == 'RF_entropy':
			results, features = ml.RandomForest_entropy(X, y,transformers, cutoff)
		elif alg == 'RF_big':
			results, features = ml.RandomForest_big(X, y,transformers, cutoff)
		elif alg == 'Bayes':
			results, features = ml.Bayes(X, y, transformers, cutoff)
		elif alg == 'SVM':
			results = ml.SVM(X, y, transformers, cutoff)
		elif alg == 'LR':
			results, features = ml.LR(X, y, transformers, cutoff)

		results_list.append([fname] + results[0:3])

		in_out.write2csv(out_dir+fname, ["fpr", "tpr", "auc", "cm"], results)
		if 'features' in locals():
			features = features.flatten()
			in_out.writeFeatures(out_dir+"features_" + fname, zip(headers[1:-1], features))
	
	# if verbose: print "      ...exporting the results"

	title = create_title(files[0].lower())
	in_out.makeROC(out_dir+"roc.png", results_list, title=title)

def create_name(f, filtr):
	if f.upper() == 'AA_KOP_TMPRL_ALL_NO_LAB':
		return 'excl. lab trends'
	if f.upper() == 'AA_KOP_TMPRL_ALL_WITH_LAB':
		return 'incl. lab trends'


	title = 'epi, ' if 'epi' in f else 'jour, '
	filtr = 'Marshal features' if filtr else 'All features'

	if 'tmprl' in f and 'group' in f:
		title = title + 'temporal, aggregated data'
	elif 'high_level' in f:
		title = title + 'regular, aggregated data'
	elif 'all' in f:
		title = title + 'regular, {}'.format(filtr)
	elif 'tmprl' in f and not 'group' in f:
		title = title + 'temporal, {}'.format(filtr)
	elif 'age' in f:
		title = title + 'age+gender data only'
	
	if title == 'epi' or title == 'jour':
		print 'table {} is not convertable'.format(f)

	return title


def create_title(f):
	title='ROC Curve'
	# if 'jour' in f:
	# 	title = title + ' using journaal'
	# else:
	# 	title = title + ' using episodes'
	if '50' in f or 'hi' in f:
		title = title + ', age group 50+' 
	elif '30' in f or 'mid' in f:
		title = title + ', age group 30+'
	else:
		title = title + ', age group 18-49'		
	return title

def chunks(l, n):
    """ Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("in_dir", help='a user specified input directory')
	parser.add_argument("out_dir", help='a user specified output directory')
	parser.add_argument('-a', '--algorithm', dest='a', nargs='+', 
		default=['CART'], choices=['LR', 'RF_big','CART','SVM'], 
		help='the algorithm to be tested with')
	parser.add_argument("-m",'--merge', default=None, dest='merge', 
		choices=['AGE18_JOUR_ALL', 'AGE30_JOUR_ALL', 'AGE50_JOUR_ALL'], 
		help='indicates if and with what we merge the queried data')

	args = parser.parse_args()

	run_experiments(args.in_dir, args.out_dir, algorithms=args.a, merge=args.merge)

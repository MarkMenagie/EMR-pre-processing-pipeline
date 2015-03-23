import util_.util as util
import util_.in_out as in_out
import algorithms as ML
from sklearn.feature_selection import SelectKBest, f_classif, chi2, VarianceThreshold
import numpy as np
from scipy.stats import pearsonr
from sklearn.metrics import roc_curve, auc

def execute(in_dir, out_dir, record_id, target_id, algorithms, feature_selection, separate_testset, in_dir2):
	'''executes the learning task on the data in in_dir with the algorithms in algorithms.
		The results are written to out_dir and subdirectories,
	    and the record_ and target_ids are used to differentiate attributes and non-attributes'''
	print '### executing learning algorithms on... ###'
	
	# get the files
	files = util.list_dir_csv(in_dir)
	if separate_testset:
		files2 = util.list_dir_csv(in_dir2)

	# stop if no files found
	if not files:
		print 'No appropriate csv files found. Select an input directory with appropriate files'
		return

	# create directory
	util.make_dir(out_dir)

	# execute each algorithm
	for alg in algorithms:
		print '...{}'.format(alg)
		set2model_instance = execute_with_algorithm(alg, files, out_dir+'/'+alg+'/', record_id, target_id, feature_selection)
		if separate_testset:
			predict_separate(alg, files2, out_dir+'/'+alg+'_test/', record_id, target_id, feature_selection, set2model_instance)
		

	# notify user
	print '## Learning Finished ##'

def execute_with_algorithm(alg, files, out_dir, record_id, target_id, feature_selection):
	'''execute learning task using the specified algorithm'''

	util.make_dir(out_dir)

	# list which will contain the results
	results_list = []	
	set2model_instance = dict()
	
	# run algorithm alg for each file f
	for f in files:

		# get base file name
		fname = in_out.get_file_name(f, extension=False)
		print ' ...{}'.format(fname)
		
		# get data, split in features/target. If invalid stuff happened --> exit
		X, y, headers = in_out.import_data(f, record_id, target_id) # assumption: first column is patientnumber and is pruned, last is target
		if type(X) == bool: return
		print '  ...instances: {}, attributes: {}'.format(X.shape[0], X.shape[1])

		# feature selection
		k = 50
		if feature_selection and X.shape[1] >= k:
			print '  ...performing feature selection'

			# subset for feature selection
			# print '   ...subsetting pos'
			# print y.shape, y[0:5], type(y[0]), type(y[1])
			# pos_target_indices = y[y==1]
			# # print pos_target_indices, pos_target_indices.shape
			# sub_pos_X = X[pos_target_indices,:]
			# sub_pos_y = np.squeeze(y[pos_target_indices])

			# # print '    ..neg'
			# neg_target_indices = y[y==0]
			# # print y[pos_target_indices].shape
			# # print y[neg_target_indices].shape

			# # print '     ..choices'
			# neg_choices = np.random.choice(y[neg_target_indices], size=sum(pos_target_indices)*50, replace=False)
			# # print neg_choices
			# sub_neg_X = X[neg_choices,:]
			# sub_neg_y = np.squeeze(y[neg_choices])

			# # print '    ... adding, ', sub_pos_X.shape[1]
			# cols = sub_pos_X.shape[1]
			# rows_pos = sub_pos_X.shape[0]
			# rows = sub_pos_X.shape[0] + sub_neg_X.shape[0]
			# sub_X = np.empty( (rows, cols) )
			# sub_X[0:rows_pos, :] = sub_pos_X
			# sub_X[rows_pos:, :] = sub_neg_X
			# sub_y = np.append(sub_pos_y, sub_neg_y)
			# # print sub_pos_X.shape
			# # print sub_neg_X.shape
			# # print sub_X.shape
			# # print sub_y.shape

			# # FS
			# transformer = SelectKBest(f_classif, k)
			# # transformer = VarianceThreshold(0.005)
			# new_sub_X = transformer.fit_transform(sub_X, sub_y)
			# best_features = np.array(transformer.scores_).argsort()[-k:][::-1]
			
			
			pearsons = []
			for i in range(X.shape[1]):
				p = pearsonr(np.squeeze(np.asarray(X[:,i])), y)
				pearsons.append(abs(p[0]))
			best_features = np.array(pearsons).argsort()[-k:][::-1]

			# print best_features
			headers = [headers[i] for i in best_features]
			new_X = X[:,best_features]
			# print new_X.shape
			# print y.shape

		else:
			new_X = X
			best_features = 'all'

		# execute algorithm
		if alg == 'DT':
			results, model = ML.CART(new_X, y, best_features, out_dir+"{}.dot".format(fname), headers)
		elif alg == 'RF':
			results, features, model = ML.RF(new_X, y, best_features, n_estimators=100)
		elif alg == 'RFsmall':
			results, features, model = ML.RF(new_X, y, best_features, n_estimators=10)
		elif alg == 'SVM':
			results, model = ML.SVM(new_X, y, best_features)
		elif alg == 'LR':
			results, features, model = ML.LR(new_X, y, best_features)

		if not results:
			return set2model_instance

		set2model_instance[fname] = (model, best_features)

		# export results
		results_list.append([fname] + results[0:3])

		in_out.save_results(out_dir+fname+'.csv', ["fpr", "tpr", "auc", "cm"], results, [sum(y),len(y)])
		if 'features' in locals():
			features = features.flatten()
			in_out.save_features(out_dir+"features_" + fname + '.csv', zip(headers[1:-1], features))
	
	in_out.save_ROC(out_dir+"roc.png", results_list, title='ROC curve')

	return set2model_instance

def predict_separate(alg, files, out_dir, record_id, target_id, feature_selection, model_info):
	'''execute learning task using the specified algorithm'''

	util.make_dir(out_dir)

	# list which will contain the results
	results_list = []	
	
	# run algorithm alg for each file f
	for f in files:

		# get base file name
		fname = in_out.get_file_name(f, extension=False)
		print ' ...{}'.format(fname)
		
		# get data, split in features/target. If invalid stuff happened --> exit
		X, y, headers = in_out.import_data(f, record_id, target_id) # assumption: first column is patientnumber and is pruned, last is target
		if type(X) == bool: return
		print '  ...instances: {}, attributes: {}'.format(X.shape[0], X.shape[1])

		best_features, model = model_info[fname]
		if best_features == 'all':
			new_X = X
		else:
			new_X = X[:,best_features]

		# execute algorithm
		y_pred = model.predict_probas(X_new)
		fpr, tpr, thresholds = roc_curve(y, y_pred[:, 1])
		mean_auc = auc(mean_fpr, mean_tpr)
		results = [fpr, tpr, mean_auc, np.zeros((2,2))]

		# export results
		results_list.append([fname] + results)

		in_out.save_results(out_dir+fname+'.csv', ["fpr", "tpr", "auc", "cm"], results, [sum(y),len(y)])
	
	in_out.save_ROC(out_dir+"roc.png", results_list, title='ROC curve')

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

	execute(args.in_dir, args.out_dir, algorithms=args.a, merge=args.merge)

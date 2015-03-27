import util_.util as util
import util_.in_out as in_out
import algorithms as ML
from sklearn.feature_selection import SelectKBest, f_classif, chi2, VarianceThreshold
import numpy as np
from scipy.stats import pearsonr
from sklearn.metrics import roc_curve, auc
from scipy import interp

def execute(in_dir, out_dir, record_id, target_id, algorithms, feature_selection, separate_testset, in_dir_test):
	'''executes the learning task on the data in in_dir with the algorithms in algorithms.
		The results are written to out_dir and subdirectories,
	    and the record_ and target_ids are used to differentiate attributes and non-attributes'''
	print '### executing learning algorithms on... ###'
	
	# get the files
	files = util.list_dir_csv(in_dir)

	# stop if no files found
	if not files:
		print 'No appropriate csv files found. Select an input directory with appropriate files'
		return

	if separate_testset:
		files_test = util.list_dir_csv(in_dir_test)
	else:
		files_test = files

	# create directory
	util.make_dir(out_dir)

	# execute each algorithm
	for alg in algorithms:
		print '...{}'.format(alg)
	
		util.make_dir(out_dir+'/'+alg+'/')
		results_list = []	
		if separate_testset:
			results_list2 = []
			util.make_dir(out_dir+'/'+alg+'_test/')

		# list which will contain the results
	
		# run algorithm alg for each file f
		for f, f_test in zip(files,files_test):
			fname = in_out.get_file_name(f, extension=False)
			print ' ...{}'.format(fname)
	
			# get data, split in features/target. If invalid stuff happened --> exit
			X, y, headers = in_out.import_data(f, record_id, target_id) # assumption: first column is patientnumber and is pruned, last is target
			if type(X) == bool: return

			# if separate_testset:
			# 	X, X_te = X
			# 	y, y_te = y
			# 	print '  ...train instances: {}, attributes: {}'.format(X.shape[0], X.shape[1])
			# 	print '  ...test instances: {}, attributes: {}'.format(X_te.shape[0], X_te.shape[1])
			# else:
			print '  ...instances: {}, attributes: {}'.format(X.shape[0], X.shape[1])

			model, best_features, results = execute_with_algorithm(alg, X, y, fname, headers, out_dir+'/'+alg+'/', record_id, target_id, feature_selection)
			results_list.append(results)

			if separate_testset:
				X, y, headers = in_out.import_data(f_test, record_id, target_id) # assumption: first column is patientnumber and is pruned, last is target
				if type(X) == bool: return
				
				print '  ...instances: {}, attributes: {} (test set)'.format(X.shape[0], X.shape[1])				

				results = predict_separate(X, y, fname, out_dir+'/'+alg+'_test/', record_id, target_id, feature_selection, model, best_features)
				results_list2.append(results)

		try:
			in_out.save_ROC(out_dir+'/'+alg+'/'+"roc.png", results_list, title='ROC curve')
		except IndexError:
			pass
		
		try:
			in_out.save_ROC(out_dir+'/'+alg+'_test/'+"roc.png", results_list2, title='ROC curve')
		except NameError:
			pass

	# notify user
	print '## Learning Finished ##'

def execute_with_algorithm(alg, X, y, fname, headers, out_dir, record_id, target_id, feature_selection):
	'''execute learning task using the specified algorithm'''

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
		return

	# set2model_instance[fname] = (model, best_features)

	# export results
	# results_list.append([fname] + results[0:3])

	in_out.save_results(out_dir+fname+'.csv', ["fpr", "tpr", "auc", "cm"], results, [sum(y),len(y)])
	if 'features' in locals():
		features = features.flatten()
		in_out.save_features(out_dir+"features_" + fname + '.csv', zip(headers[1:-1], features))
	
	return model, best_features, [fname] + results[0:3]

def predict_separate(X, y, fname, out_dir, record_id, target_id, feature_selection, model, best_features):
	'''execute learning task using the specified algorithm'''
	print '  ...testing on new data'
	
	# select the feature selected attribute only
	if best_features == 'all':
		new_X = X
	else:
		new_X = X[:,best_features]

	# execute algorithm
	y_pred = model.predict_proba(new_X)
	fpr, tpr, _ = roc_curve(y, y_pred[:, 1])
	mean_fpr = np.linspace(0, 1, 100)
	mean_tpr = interp(mean_fpr, fpr, tpr)
	mean_auc = auc(fpr, tpr)
	results = [mean_fpr, mean_tpr, mean_auc, np.zeros((2,2))]
	in_out.save_results(out_dir+fname+'.csv', ["fpr", "tpr", "auc", "cm"], results, [sum(y),len(y)])

	results = [fname] + results[0:3]
	return results



import util_.util as util
import util_.in_out as in_out
import algorithms as ML
from sklearn.feature_selection import SelectKBest, chi2

def execute(in_dir, out_dir, record_id, target_id, algorithms, feature_selection):
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

	# create directory
	util.make_dir(out_dir)

	# execute each algorithm
	for alg in algorithms:
		print '...{}'.format(alg)
		execute_with_algorithm(alg, files, out_dir+'/'+alg+'/', record_id, target_id, feature_selection)

	# notify user
	print '## Learning Finished ##'

def execute_with_algorithm(alg, files, out_dir, record_id, target_id, feature_selection):
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

		# feature selection
		k = 250
		if feature_selection and X.shape[1] >= k:
			transformers = [('kbest', SelectKBest(chi2, 250))]
		else:
			transformers = []

		# execute algorithm
		if alg == 'DT':
			results = ML.CART(X, y, transformers, out_dir+"{}.dot".format(fname), headers)
		elif alg == 'RF':
			results, features = ML.RF(X, y, transformers)
		elif alg == 'SVM':
			results = ML.SVM(X, y, transformers)
		elif alg == 'LR':
			results, features = ML.LR(X, y, transformers)

		if not results:
			return

		# export results
		results_list.append([fname] + results[0:3])

		in_out.save_results(out_dir+fname+'.csv', ["fpr", "tpr", "auc", "cm"], results)
		if 'features' in locals():
			features = features.flatten()
			in_out.save_features(out_dir+"features_" + fname + '.csv', zip(headers[1:-1], features))
	
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

import util_.util as util

def execute(in_dir, out_dir, record_id, target_id, algorithms):
	'''executes the learning task on the data in in_dir with the algorithms in algorithms.
		The results are written to out_dir and subdirectories,
	    and the record_ and target_ids are used to differentiate attributes and non-attributes'''
	
	files = util.list_dir_csv(in_dir)
	if not files:
		print 'No approriate csv files found. Select an input directory with appropriate files'
		return

	for alg in algorithms:
		run_with_algorithm(alg, in_dir, out_dir+'/'+alg+'/', record_id, target_id)

	print '## Learning Finished ##'

def run_with_algorithm(c, alg, files, out_dir, ):
	make_dirs(out_dir)
	results_list = []	
	for f in files:
		fname = f.split('/')[-1]
		fname = create_name(f.lower(), c[4])
		
		# get data, split in features/target
		execute_query_with_tbl(c[0],f, c[3], c[4])
		X, y, headers = in_out.cursor2array(c) # assumption: first column is patientnumber and is pruned, last is target
	
		# run algorithm
		if alg == 'DT':
			results = ml.CART(X,y,transformers, out_dir+"/{}.dot".format(fname), headers,cutoff)
		elif alg == 'RF_big':
			results, features = ml.RandomForest_big(X, y,transformers, cutoff)
		elif alg == 'SVM':
			results = ml.SVM(X, y, transformers, cutoff)
		elif alg == 'LR':
			results, features = ml.LR(X, y, transformers, cutoff)

		# export results
		results_list.append([fname] + results[0:3])

		in_out.write2csv(out_dir+fname, ["fpr", "tpr", "auc", "cm"], results)
		if 'features' in locals():
			features = features.flatten()
			in_out.writeFeatures(out_dir+"features_" + fname, zip(headers[1:-1], features))
	
	in_out.makeROC(out_dir+"roc.png", results_list, title='ROC curve')

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

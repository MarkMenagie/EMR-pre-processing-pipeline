import util_.util as util
import util_.in_out as io
from prep.EnrichProcesses import StandardEnrichProcess
from math import sqrt
import scipy.stats as stats

class FrequencyCounter():

	def __init__(self, data_dir, export_dir, ALPHA):
		'''set in- and output directories, and which enrichment files 
			are simply skipped and not further pruned (only renamed)'''
		self.data_dir = data_dir
		self.export_dir = export_dir
		self.ALPHA = ALPHA

	def execute(self, subdirs, preprocess_args, needs_processing):
		'''process the enrichment files in the specified folder'''
		self.import_data(preprocess_args, needs_processing)
		self.count()
		self.significance_test()

		dirs = {subdir : (self.export_dir + '/' + subdir + '/') for subdir in subdirs}
		
		if 'atc' in dirs:
			self.export(dirs['atc'], 'effect')
			self.export(dirs['atc'], 'indication')
			# self.export(dirs['atc'], 'ingredient')
		if 'icpc' in dirs:
			self.export(dirs['icpc'], 'manifestationof')
			self.export(dirs['icpc'], 'association')

	def import_data(self, preprocess_args, needs_processing):
		sep = StandardEnrichProcess(*preprocess_args)
		sep.process(needs_processing)
		self.process_instance = sep

	def count(self):
		'''count each code among all files'''
		headers = self.process_instance.headers
		id2data = self.process_instance.id2data
		self.abstraction2counts = dict()
		count = 0
		count_pos = 0 
		for i, h in enumerate(headers):
			if h.lower() in ['id', 'target', 'age', 'gender']:
				continue
			for ID in id2data:
				add = int(id2data[ID]['data'][i])
				count += add
				if id2data[ID]['data'][-1] != 'negative':
					count_pos += add
			self.abstraction2counts[h] = (count, count_pos)

		# for a in self.abstraction2counts:
		# 	if self.abstraction2counts[a] != (0, 0):
		# 		print self.abstraction2counts[a]
	
	def significance_test(self):
		'''test significance of each code among all files'''
		# remove keys whose ratio between the total and CRC-positive counts are over a threshold
		for key in self.abstraction2counts:
			# number of  instances
			if 'effect' in key or 'indication' in key or 'ingredient' in key:
				n1 = float(self.process_instance.num_med)
				n2 = float(self.process_instance.num_med_pos)
			elif 'manifestationof' in key or 'association' in key:
				n1 = float(self.process_instance.num_cons)
				n2 = float(self.process_instance.num_cons_pos)				
			else:
				print 'error. unknown abstraction {} in FrequencyCounter.py, line 50ish'.format(key)
				exit()

			# number of counts for total and positive categories
			total_count, pos_count = self.abstraction2counts[key]

			# this snippet essentially corrects for double occurrences of abstractions in a single code (e.g. 2x 'Rash' in atc code A01B234)
			if total_count > n1: 
				total_count = n1
			if pos_count > n2: 
				pos_count = n2

			# proportions
			p1 = total_count / n1
			p2 = pos_count / n2

			# perform statistical test (see http://stattrek.com/hypothesis-test/difference-in-proportions.aspx)
			p = ( (p1*n1) + (p2*n2) ) / (n1+n2)  # pooled sample statistic
			# print key, p, n1, n2, p1, p2
			SE = sqrt( p*(1-p) * ( 1./n1 + 1./n2) ) # standard error
			if SE == 0:
				SE = 0.00000001
			Z = (p1-p2) / SE # Z-score
			P_value = stats.norm.sf(Z)*2 # *2 because two-tailed
			self.abstraction2counts[key] = P_value

	def export(self, folder, suffix):
		'''export significant abstractions with the specified suffix to a new file'''
		rows = io.read_csv(folder + suffix + '.csv')
		code2abstractions = {row[0] : row[1:] for row in rows}

		out = io.write_csv(folder + suffix + '_frequent.csv')
		for key, vals in code2abstractions.iteritems(): 
			frequent_vals = []
			for abstraction in vals:
				abstraction = abstraction+'_'+suffix
				if abstraction in self.abstraction2counts and self.abstraction2counts[abstraction] < self.ALPHA:
					frequent_vals.append(abstraction)
			if len(frequent_vals) > 0:
				out.writerow([key] + frequent_vals)

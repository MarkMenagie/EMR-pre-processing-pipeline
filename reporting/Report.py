import util_.in_out as io
from operator import itemgetter

class Report():
	'''provides the functionality to compile and export a report
		using various files resulting from previous steps in the process'''

	def __init__(self, f1, f2, f3, f_out, feature_threshold):
		'''initialize the report object'''
		self.f_general = f1
		self.f_data = f2
		self.f_predictors = f3
		self.f_out = f_out
		self.feature_threshold = feature_threshold

		self.compiled_result = dict()

	def compile(self):
		'''compile the individual parts of the report'''

		# compile general segment
		rows = io.read_csv(self.f_general)
		self.compiled_result['general'] = self.compile_general(rows)

		# compile header
		headers = ['predictor', '# CRC', '% CRC', '# No CRC', '% No CRC', '# Total', '% Total']
		self.compiled_result['headers'] = headers

		# compile results
		predictors = io.read_csv(self.f_predictors)
		data = io.read_csv(self.f_data)
		self.compiled_result['data'] = self.compile_data(predictors, data)

	def compile_general(self, rows):
		'''compile the general segment'''

		result = dict()

		# skip 8 rows
		for i in range(8):
			try:
				rows.next()
			except IOError, e:
				print e, 'did you get the right file?'
				exit()

		# process info on 9th row
		stats = rows.next()
		self.num_CRC = int(float(stats[0]))
		self.num_Total = int(float(stats[1]))
		self.num_non_CRC = self.num_Total - self.num_CRC

		# save in dict
		result['headers'] = ['CRC', 'No CRC', 'Total']
		result['stats'] = [self.num_CRC, self.num_non_CRC, self.num_Total]
		return result

	def compile_data(self, predictors, data):
		'''compile data of relevant predictors'''

		# get relevant predictors
		relevant_predictors = [p[0].lower() for p in predictors if abs(float(p[1])) >= self.feature_threshold]

		# get indices of the relevant predictors
		headers = data.next()
		relevant_tuples = [(i, h.lower()) for i, h in enumerate(headers) if h.lower() in relevant_predictors]

		# using the relevant indices, only keep the important data in memory
		relevant_data = dict()
		for d in data:
			# get 1 (CRC) or 0 (no CRC)
			target = int(d[-1])

			# get all relevant data of the instance
			relevant_instance_data = [int(d[i]) for i, h in relevant_tuples]

			# for every attribute, if the current instance has it at least once, add to the result dictionary
			if target in relevant_data:
				relevant_data[target] = [attr+1 if relevant_instance_data[i] > 0 else attr for i, attr in enumerate(relevant_data[target])]
			else:
				relevant_data[target] = [1 if relevant_instance_data[i] > 0 else 0 for i, attr in enumerate(relevant_instance_data)]

		# make it suitable for file output / human readable
		transposed_result = []
		for i, h in enumerate(relevant_tuples):

			# calc number of occurrences and percentage relative to population
			num_pos = relevant_data[1][i]
			per_pos = float(num_pos) / self.num_CRC *100
			num_neg = relevant_data[0][i]
			per_neg = float(num_neg) / self.num_non_CRC *100
			num_tot = num_pos + num_neg
			per_tot = float(num_tot) / self.num_Total *100

			# make list and append
			lst = [h[1], num_pos, per_pos, num_neg, per_neg, num_tot, per_tot]
			transposed_result.append(lst)

		# sort result by occurrence in the CRC column
		transposed_result.sort(key=itemgetter(1), reverse=True)
		return transposed_result

	def export(self):
		'''exports the result to the specified file'''
		# open file for writing
		out = io.write_csv(self.f_out)

		# write sources
		out.writerow(['general source', 'predictor source', 'data source'])
		out.writerow([self.f_general, self.f_predictors, self.f_data])
		out.writerow([])

		# write general stuff
		out.writerow(self.compiled_result['general']['headers'])
		out.writerow(self.compiled_result['general']['stats'])
		out.writerow([])

		# write headers to file
		out.writerow(self.compiled_result['headers'])

		# write individual results to file
		for row in self.compiled_result['data']:
			out.writerow(row)

if __name__ == '__main__':
	import sys
	args = sys.argv[1:]
	report = Report(args[0], args[1], args[2], args[3])
	report.compile()
	report.export()
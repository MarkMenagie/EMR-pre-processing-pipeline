import re

from StandardProcess import StandardProcess
from date_math import str2date, four_weeks
import util_.util as util
import abstracts

class NonMarshallProcess(StandardProcess):
	'''class describing standard way of preprocessing 
		the data by counting occurrences of data concepts'''

	def insert_data(self, rows, headers, code_column, date_column, regex_string, limit, suffix='', incorporate_SOEP=False):
		'''inserts data from the specified csv and corresponding columns'''

		# make convenient reference to the dictionary
		dct = self.id2data

		# # get data and corresponding headers
		# rows, headers = util.import_data(f, delim=self.delim)

		# get the index of the relevant columns
		ID_idx = headers.index(self.ID_column)
		code_idx = headers.index(code_column)
		date_idx = headers.index(date_column[0])
		
		if suffix == 'lab_results':
			val_idx = headers.index('waarde')
			min_idx = headers.index('referentie_minimum')
			max_idx = headers.index('referentie_maximum')
		if incorporate_SOEP:
			SOEP_idx = headers.index(incorporate_SOEP)
		
		# get the right suffix to append for the attribute name
		if suffix == '':
			suffix = code_column

		# regex pattern to match (ATC/ICPC standards)
		pattern = re.compile(regex_string)

		# keep track of number of times the row is attributed to a positive CRC patient (or patient where the target instance = 'positive')
		num_pos = 0
		num_total = 0

		# iterate over all instances, making a new dict with the new attributes as keys
		attribute2ids = dict()
		for row in rows:
			original_code = row[code_idx]
			if original_code == None:
				continue
			truncated_code = self.generate_code(original_code, limit)
			if truncated_code == None:
				continue

			### is in Marshall Predictors check ###
			### if it is a marshall predictor, we skip this line.
			if self.marshall_predictor(truncated_code, code_column):
				continue
			num_total+=1

			# if key is not in the data dictionary, we skip it
			key = int(row[ID_idx])
			if not key in dct:
				continue

			if dct[key]['CRC_dates'][0] != 'negative':
				num_pos+=1

			# init other vars
			date = str2date(row[date_idx], give_default_begin=True)
			begin = dct[key]['CRC_dates'][3]
			end = dct[key]['CRC_dates'][4]
			if code_column == 'specialisme':
				end = end - four_weeks()

			if suffix == 'lab_results':
				val, min_val, max_val = self.make_lab_values(row[val_idx], row[min_idx], row[max_idx])
				if val == '':
					continue

			# if in the required interval and code is valid
			if (begin <= date and date <= end) and pattern.match(truncated_code):
				
				# if we do not care about SOEPcode (always except for journaal case) or the SOEPcode is E
				if (not incorporate_SOEP) or (incorporate_SOEP and row[SOEP_idx] == 'E'):
				
					if suffix == 'lab_results': # if we prepare for lab result abstraction
						if not 'ID2abstractions' in locals():
							# dict (patient) of dict (lab measurement name) of list of tuples (all value/date combinations of measurement)
							ID2abstractions = dict()
						
						util.init_key(ID2abstractions, key, dict())
						util.init_key(ID2abstractions[key], original_code, [])

						ID2abstractions[key][original_code].append((date, val))

						if '' not in [val, min_val, max_val]:
							attr = abstracts.get_value(val, min_val, max_val, original_code)

							# check if attribute name and ID instance already exist, if not, make them
							util.init_key(attribute2ids, attr, dict())
							util.init_key(attribute2ids[attr], key, 0)

							# add 1 to the occurrence of the attribute in the instance
							attribute2ids[attr][key] += 1

					else: # else no lab result collection, regular aggregation
						# generate attribute names
						attributes = self.generate_attributes(original_code, limit, suffix, src=code_column)
						
						# this loop allows multiple attributes to be created in the previous code line
						# this allows for other classes to subclass this class, e.g. StandardEnrichProcess
						for attr in attributes:
							# print truncated_code, attr
							# check if attribute name and ID instance already exist, if not, make them
							util.init_key(attribute2ids, attr, dict())
							util.init_key(attribute2ids[attr], key, 0)

							# add 1 to the occurrence of the attribute in the instance
							attribute2ids[attr][key] += 1

		if suffix == 'lab_results': # do funky stuff with trends and abstractions
			# convert to trends PER lab result
			for ID in ID2abstractions:
				# print ID2abstractions[ID]
				for k, points in ID2abstractions[ID].iteritems():
					
					# the values are sorted before abstraction
					points = sorted(list(set(points)))

					# abstract the values and count the occurrences per measurement-trend per patient
					# if only 1 measurement was done, we cannot do time series analysis
					if len(points) > 1 and ID in dct: 
						abstractions = abstracts.get_trends(k, points)
						for attr in abstractions:
							attr = attr[0] # get the state
							util.init_key(attribute2ids, attr, dict())
							util.init_key(attribute2ids[attr], ID, 0)
							attribute2ids[attr][ID] += 1
		# print len(attribute2ids)
		# print attribute2ids.keys()[0:5]
		
		# add data to each instance
		for ID in dct:
			data = dct[ID]['data']

			for id2occurrences in attribute2ids.values():
				
				# if patient has occurrences for the attribute, add that number, else add 0
				if ID in id2occurrences: 
					data.append(id2occurrences[ID])
				else:
					data.append(0)

		# return the keys to be used as headers when writing the processed data
		return attribute2ids.keys(), num_total, num_pos

	def marshall_predictor(self, code, src):
		is_med_predictor = (src == 'atc_code') and code in ['A06','A07','B03']
		is_consult_predictor = (src == 'icpc') and code in [
			'D01','D02','D06','D08','D11','D12','D15','D16','D18','D24','D93',
			'K93','K94',
			'T07','T08','T82','T89','T90','T92',
			'G04']
		is_lab_predictor = (src == 'codenorm') and code in [
			'HB','HBA1','HBA2',
			'MCH','MCHC','MCV'
			'OCCULTBLOE', 'OCBIDF']
		return is_med_predictor or is_consult_predictor or is_lab_predictor

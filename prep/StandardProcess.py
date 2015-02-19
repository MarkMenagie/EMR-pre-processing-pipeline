import re

from PreProcess import PreProcess
from date_math import str2date
import util_.util as util

class StandardProcess(PreProcess):

	def insert_data(self, f, code_column, date_column, regex_string, limit, suffix='', incorporate_SOEP=False):
		'''inserts data from the specified csv and corresponding columns'''

		# make convenient reference to the dictionary
		dct = self.id2data

		# get data and corresponding headers
		rows, headers = util.import_data(f, delim=self.delim)

		# get the index of the relevant columns
		ID_idx = headers.index(self.ID_column)
		code_idx = headers.index(code_column)
		date_idx = headers.index(date_column[0])
		if incorporate_SOEP:
			SOEP_idx = headers.index(incorporate_SOEP)
		
		# get the right suffix to append for the attribute name
		if suffix == '':
			suffix = code_column

		# regex pattern to match (ATC/ICPC standards)
		pattern = re.compile(regex_string)

		# iterate over all instances, making a new dict with the new attributes as keys
		attribute2ids = dict()
		for row in rows:

			# if key is not in the data dictionary, we skip it
			key = int(row[ID_idx])
			if not key in dct:
				continue

			# init other vars
			date = str2date(row[date_idx])
			begin = dct[key]['CRC_dates'][3]
			end = dct[key]['CRC_dates'][4]
			code = row[code_idx].upper().strip()[0:limit]

			# if in the required interval and code is valid
			if (begin <= date and date <= end) and pattern.match(code):
				
				if (not incorporate_SOEP) or (incorporate_SOEP and row[SOEP_idx] == 'E'):
				
					# generate attribute name
					attribute = code + '_' + suffix
					
					# check if attribute name and ID instance already exist, if not make them
					util.init_key(attribute2ids, attribute, dict())
					util.init_key(attribute2ids[attribute], key, 0)

					# add 1 to the occurrence of the attribute in the instance
					attribute2ids[attribute][key] += 1

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
		return attribute2ids.keys()

if __name__ == '__main__':
	dct = dict()
	dct['in_dir'] = '/Users/Reiny/Documents/UI_CRC/playground'
	dct['delimiter'] = ','
	dct['out_dir'] = '/Users/Reiny/Documents/UI_CRC/out'
	dct['min_age'] = 18
	dct['max_age'] = 150
	dct['begin_interval'] = int(365./52*38)
	dct['end_interval'] = int(365./52*12)
	dct['ID_column'] = 'patientnummer'

	sp = StandardProcess()
	sp.process(dct['in_dir'],
				dct['delimiter'],
				dct['out_dir'],
				dct['ID_column'],
				dct['min_age'],
				dct['max_age'],
				[int(dct['end_interval']), int(dct['begin_interval'])])
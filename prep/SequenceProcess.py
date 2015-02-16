from operator import attrgetter
import re

from PreProcess import PreProcess
from StateInterval import StateInterval
from date_math import get_dates, str2date
import util

class SequenceProcess(PreProcess):

	def insert_data(self, f, code_column, date_column, regex_string, limit, suffix='', incorporate_SOEP=False):
		'''inserts data from the specified csv and corresponding columns'''

		# make convenient reference to the dictionary
		dct = self.id2data

		# get data and corresponding headers
		rows, headers = util.import_data(f, delim=self.delim)

		# get the index of the relevant columns
		ID_idx = headers.index(self.ID_column)
		code_idx = headers.index(code_column)
		b_date_idx = headers.index(date_column[0])
		e_date_idx = headers.index(date_column[1])
		if incorporate_SOEP:
			SOEP_idx = headers.index(incorporate_SOEP)

		# get the right suffix to append for the attribute name
		if suffix == '':
			suffix = code_column

		# regex pattern to match (ATC/ICPC standards)
		pattern = re.compile(regex_string)

		# iterate over all instances, making a new dict with the new attributes as keys
		for row in rows:

			# if key is not in the data dictionary, we skip it
			key = int(row[ID_idx])
			if not key in dct:
				continue

			# init other vars
			b_date = str2date(row[b_date_idx], give_default_begin=True) # begin of event
			e_date = str2date(row[e_date_idx], give_default_end=True) # end of event
			b_reg = dct[key]['CRC_dates'][3] # beginning of registration
			e_reg = dct[key]['CRC_dates'][4] # ending of registration
			code = row[code_idx].upper().strip()[0:limit] + '_' + suffix

			# if in the required interval (either beginninf or ending date) AND code is valid
			if ( (b_reg <= b_date and b_date <= e_reg) or (b_reg <= e_date and e_date <= e_reg) ) and pattern.match(code):
				
				# if we need to take the SOEP code of consuls into account
				if (not incorporate_SOEP) or (incorporate_SOEP and row[SOEP_idx] == 'E'):
				
					# insert a StateInterval object with the specified parameters
					self.insert_state_interval(key, code, b_date, e_date)

		# to satisfy return value requirement for  the method 'process' in the superclass
		return []
			
	def insert_state_interval(self, key, state, begin, end):
		sequence = self.id2data[key]['data']
		SI = StateInterval(state, begin, end)
		sequence.append(SI)

	def sort_sequences(self):
	 	'''sort each state sequence (= 1 per patient) consisting of state intervals
		 	order of sort is: begin date->end date->lexical order of state name'''
		for k in self.id2data:
			sequence = self.id2data[k]
			static_seq = sequence[0:2] # gender/age
			crc = [sequence[2]]
			dynamic_seq = sequence[3:]
			dynamic_seq.sort(key=attrgetter('begin', 'end', 'state'))
			self.id2data[k] = static_seq + dynamic_seq + crc

if __name__ == '__main__':
	import sys

	in_dir = sys.argv[1]
	out_dir = sys.argv[2]
	age_range = (30,150)

	seq_p = SequenceProcess()
	seq_p.process(in_dir, out_dir, age_range)
import re
from date_math import generate_patient_interval, generate_random_patient_interval, str2date
from util_.in_out import write_csv
import util_.util as util

class PreProcess():

	def __init__(self, in_dir, delim, out_dir, ID_column, min_age, max_age, interval):
		self.in_dir = in_dir
		self.delim = delim
		self.out_dir = out_dir
		self.ID_column = ID_column
		self.min_age = min_age
		self.max_age = max_age
		self.interval = interval
		self.id2data = dict()

	def insert_data(self, f, code_column, date_column, regex_string, limit, suffix='', incorporate_SOEP=False):
		'''abstract method to be implemented by subclass'''
		print 'abstract method "insert_data" called'

	def	save_output(self):
		'''saves processed data to the specified output directory'''
		print 'abstract method "save_output" called'
	
	def process(self, needs_processing):
		'''converts all input csv's to usable data'''

		# get all csv's in the input folder
		files = util.list_dir_csv(self.in_dir)

		# put the IDs of the 'main' file in a dict
		ID_f = util.select_file(files, 'patient')
		headers = self.get_IDs(ID_f)

		# add CRC value to each patient
		CRC_f = util.select_file(files, 'journaal')
		self.get_CRC_occurrences(CRC_f)

		# randomize dates
		self.insert_data_intervals()

		# gather data from medication csv
		if 'medication' in needs_processing and needs_processing['medication']:
			med_f = util.select_file(files, 'medicatie')
			med_headers = self.insert_data(
									med_f, 
									'atc_code', 
									['voorschrijfdatum', 'voorschrijfdatum'], 
									'[A-Z][0-9][0-9]', 3,
									suffix='atc')
			headers = headers + med_headers

		# gather data from consult csv
		if 'consults' in needs_processing and needs_processing['consults']:
			consult_f = util.select_file(files, 'journaal')
			consult_headers = self.insert_data(
									consult_f, 
									'icpc', 
									['datum', 'datum'], 
									'[A-Z][0-9][0-9]', 3,
									incorporate_SOEP='soepcode')
			headers = headers + consult_headers

		# gather data from referral csv
		if 'referrals' in needs_processing and needs_processing['referrals']:
			ref_f = util.select_file(files, 'verwijzing')
			ref_headers = self.insert_data(
									ref_f, 
									'specialisme', 
									['datum', 'datum'], 
									'.*', None)
			headers = headers + ref_headers

		# gather data from comorbidity csv
		if 'comorbidity' in needs_processing and needs_processing['comorbidity']:
			comor_f = util.select_file(files, 'comorbiditeit')
			comor_headers = self.insert_data(
									comor_f, 
									'omschrijving', 
									['begindatum', 'einddatum'],
									'.+', None,
									suffix='comorbiditeit')
			headers = headers + comor_headers

		# gather data from lab results csv
		if 'lab_results' in needs_processing and needs_processing['lab_results']:
			lab_f = util.select_file(files, 'bepaling')
			lab_headers = self.insert_data(
									lab_f, 
									'code', 
									['datum', 'datum'], 
									'.+', None,
									suffix='lab_results')
			headers = headers + lab_headers

		# move CRC indicator to end of each instance data list
		self.move_target_to_end_of_list()
		
		# append target element to headers, add to class var
		headers.append('target')
		self.headers = headers

	def get_IDs(self, f):
		'''sets all IDs as keys to a dict. Additionally adds gender/age data
			and date registration data'''

		# get data and corresponding headers
		rows, headers = util.import_data(f, delim=self.delim)

		# get the index of the relevant columns
		ID_idx = headers.index(self.ID_column)
		age_idx = headers.index('geboortedatum')
		gender_idx = headers.index('geslacht')
		begin_idx = headers.index('inschrijfdatum')
		end_idx = headers.index('uitschrijfdatums')

		# pair IDs with a dict corresponding to data and dates
		for row in rows:
			
			# key is ID
			key = int(row[ID_idx])

			# skip if instance is outside the specified age limits
			ID_age = 2011 - int(row[age_idx])
			if ID_age < self.min_age or ID_age > self.max_age:
				continue

			# val is a new dict with keys 'data' and 'dates',
			# containing the processed data and registration dates, respectively
			val = dict()
			val['data'] = ['negative', key, ID_age, row[gender_idx]]

			registration = str2date(row[begin_idx])
			unregistration = str2date(row[end_idx], ymd=False) if row[end_idx].strip() != '' else str2date('2050-12-31')
			val['CRC_dates'] = ['negative', registration, unregistration]
			
			# add key/value pair
			self.id2data[key] = val

		return ['ID', 'age', 'gender']

	def get_CRC_occurrences(self, f):
		'''sets all CRC cases to initial diagnosis date values in 
			id2data[patient][CRC_dates][0]'''

		# get data and corresponding headers
		rows, headers = util.import_data(f, delim=self.delim)

		# get the index of the relevant columns
		ID_idx = headers.index(self.ID_column)
		CRC_idx = headers.index('icpc')
		date_idx = headers.index('datum')

		# regex pattern to match = D75 (CRC)
		CRC_pattern = re.compile('D75')

		# iterate over all data to check for CRC cases
		for row in rows:
			
			# get key and if it's in the dict, the current corresponding CRC value
			key = int(row[ID_idx])
			if key in self.id2data:
				CRC = self.id2data[key]['CRC_dates'][0]

				# get ICPC code and its date
				code = row[CRC_idx].strip().upper()[0:3]
				code_date = row[date_idx]

				# add CRC case if code matches, AND corresponding date is earlier than the currently recorded
				if CRC_pattern.match(code) and (CRC == 'negative' or CRC > str2date(code_date)):
					self.id2data[key]['CRC_dates'][0] = str2date(code_date)
					self.id2data[key]['data'][0] = 'positive'

	def insert_data_intervals(self):
		'''per data instance, gets the intervals used within which the data is regarded'''

		# iterate over dictionary
		to_remove = []
		for key, d in self.id2data.iteritems():
			date_info = d['CRC_dates']

			# if the patient has no CRC, we randomize an interval. Else we pick exact dates
			if date_info[0] == 'negative':
				result = generate_random_patient_interval(date_info[1], date_info[2], self.interval)
			else:
				result = generate_patient_interval(date_info[1], date_info[0], self.interval)
			
			# if we were able to take an interval, append to date_info
			if result:
				date_info.append(result[0])
				date_info.append(result[1])
			else: # else set up for removal
				to_remove.append(key)

		# remove all keys in the dct for which an interval could not be generated
		for key in to_remove:
			del self.id2data[key] 

	def move_target_to_end_of_list(self):
		'''moves first data value to end of list for each instance in dictionary d'''
		for k in self.id2data:
			data = self.id2data[k]['data']
			data.append(data.pop(0))

	def	save_output(self, benchmark=False, include_headers=True, sub_dir='', name='unnamed'):
		'''saves processed data to the specified output directory'''

		# possibly make new directories
		out_dir = self.out_dir + '/' + sub_dir + '/'
		util.make_dir(out_dir)

		f_out = out_dir + name + '.csv'
		out = write_csv(f_out)

		# write headers if required
		if include_headers:
			if not benchmark:
				out.writerow(self.headers)
			else:
				out.writerow(self.headers[0:3] + self.headers[-1:])

		# write data
		for value in self.id2data.values():
			data = value['data']
			if benchmark:
				data = data[0:3] + data[-1:]
			out.writerow(data)
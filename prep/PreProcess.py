import re
from date_math import generate_patient_interval, generate_random_patient_interval, str2date
from util_.in_out import write_csv
import util_.util as util
import util_.sql as sql

class PreProcess():
	'''abstract class describing basic functionality of the preprocessing phase'''

	def __init__(self, in_dir, delim, out_dir, ID_column, min_age, max_age, interval, from_sql):
		self.in_dir = in_dir
		self.delim = delim # delimiter of input file (default ',')
		self.out_dir = out_dir
		self.ID_column = ID_column # name of the ID of a data instance
		self.min_age = min_age
		self.max_age = max_age 
		self.interval = interval # interval of data we deem relevant
		self.id2data = dict() # dict describing all data instances
		self.from_sql = from_sql

	def insert_data(self, f, code_column, date_column, regex_string, limit, suffix='', incorporate_SOEP=False):
		'''abstract method to be implemented by subclass'''
		print 'abstract method "insert_data" called by', type(self)

	def process(self, needs_processing):
		'''process using the specified source'''
		if self.from_sql:
			result = self.process_sql(needs_processing)
		else:
			result = self.process_csv(needs_processing)
		return result

	def process_sql(self, needs_processing):
		'''converts the specified sql tables to usable data'''

		# connect to database and get a cursor handle
		cursor = util.sql_connect().cursor()
		
		# put the IDs of the 'main' file in a dict
		headers = self.get_IDs_sql(cursor)

		# add CRC value to each patient
		self.get_CRC_occurrences_sql(cursor)

		# randomize dates
		self.insert_data_intervals()

		# gather data from medication csv
		if 'medication' in needs_processing and needs_processing['medication']:
			fields = ['patientnummer', 'atc_code', 'voorschrijfdatum'] # make headers
			fields_str = ','.join(fields) # fields to comma-separated string

			# build query, execute
			query = 'SELECT {} FROM medicaties'.format(fields_str)
			cursor.execute(query)

			med_headers, self.num_med, self.num_med_pos = self.insert_data(
									cursor, fields, 
									'atc_code', 
									['voorschrijfdatum', 'voorschrijfdatum'], 
									'[A-Z][0-9][0-9]', 3,
									suffix='atc')
			headers = headers + med_headers

		# gather data from consult csv
		if 'consults' in needs_processing and needs_processing['consults']:
			fields = ['patientnummer', 'soepcode', 'icpc', 'datum'] # make headers
			fields_str = ','.join(fields) # fields to comma-separated string

			# build query, execute
			query = 'SELECT {} FROM journalen'.format(fields_str)
			cursor.execute(query)

			consult_headers, self.num_cons, self.num_cons_pos = self.insert_data(
									rows, fields, 
									'icpc', 
									['datum', 'datum'], 
									'[A-Z][0-9][0-9]', 3,
									incorporate_SOEP='soepcode')
			headers = headers + consult_headers

		# gather data from referral csv
		if 'referrals' in needs_processing and needs_processing['referrals']:
			fields = ['patientnummer', 'specialisme', 'datum'] # make headers
			fields_str = ','.join(fields) # fields to comma-separated string

			# build query, execute
			query = 'SELECT {} FROM doorverwijzingen'.format(fields_str)
			cursor.execute(query)

			ref_headers,_,_ = self.insert_data(
									rows, fields, 
									'specialisme', 
									['datum', 'datum'], 
									'.*', None)
			headers = headers + ref_headers

		# gather data from comorbidity csv
		if 'comorbidity' in needs_processing and needs_processing['comorbidity']:
			fields = ['patientnummer', 'omschrijving', 'begindatum', 'einddatum'] # make headers
			fields_str = ','.join(fields) # fields to comma-separated string

			# build query, execute
			query = 'SELECT {} FROM journalen'.format(fields_str)
			cursor.execute(query)

			comor_headers,_,_ = self.insert_data(
									rows, fields, 
									'omschrijving', 
									['begindatum', 'einddatum'],
									'.+', None,
									suffix='comorbiditeit')
			headers = headers + comor_headers

		# gather data from lab results csv
		if 'lab_results' in needs_processing and needs_processing['lab_results']:
			fields = ['patientnummer', 'code', 'datum'] # make headers
			fields_str = ','.join(fields) # fields to comma-separated string

			# build query, execute
			query = 'SELECT {} FROM journalen'.format(fields_str)
			cursor.execute(query)

			lab_headers, self.num_lab, self.num_lab_pos = self.insert_data(
									rows, fields, 
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

	def get_IDs_sql(self, cursor):
		'''get the record IDs using SQL'''
		
		# make headers (hardcoded for now)
		fields = ['geboortedatum', 'geslacht', 'inschrijfdatum', 'uitschrijfdatums', 'patientnummer']
		fields_str = ','.join(fields)

		# build query, execute
		query = 'SELECT {} FROM PATIENTEN'.format(fields_str)
		cursor.execute(query)

		# start filling self.id2data
		return self.get_IDs(cursor, fields)

	def get_CRC_occurrences_sql(self, cursor):
		'''set CRC cases using sql'''

		# make headers (hardcoded for now)
		fields = ['soepcode', 'icpc', 'datum', 'contactsoort', 'episode_omschrijving', 'episode_icpc', 'patientnummer']
		fields_str = ','.join(fields)

		# build query, execute
		query = "SELECT {} FROM journalen WHERE soepcode = 'E' ".format(fields_str)
		cursor.execute(query)

		# further fill self.id2data
		self.get_CRC_occurrences(cursor, fields)

	def process_csv(self, needs_processing):
		'''converts the specified csv's to usable data'''

		# get all csv's in the input folder
		files = util.list_dir_csv(self.in_dir)

		# put the IDs of the 'main' file in a dict
		ID_f = util.select_file(files, 'patient')
		rows, fields = util.import_data(ID_f, delim=self.delim)
		headers = self.get_IDs(rows, fields)

		# add CRC value to each patient
		CRC_f = util.select_file(files, 'journaal')
		rows, fields = util.import_data(CRC_f, delim=self.delim)
		self.get_CRC_occurrences(rows, fields)

		# randomize dates
		self.insert_data_intervals()

		# gather data from medication csv
		if 'medication' in needs_processing and needs_processing['medication']:
			med_f = util.select_file(files, 'medicatie')
			rows, fields = util.import_data(med_f, delim=self.delim)
			med_headers, self.num_med, self.num_med_pos = self.insert_data(
									rows, fields, 
									'atc_code', 
									['voorschrijfdatum', 'voorschrijfdatum'], 
									'[A-Z][0-9][0-9]', 3,
									suffix='atc')
			headers = headers + med_headers

		# gather data from consult csv
		if 'consults' in needs_processing and needs_processing['consults']:
			consult_f = util.select_file(files, 'journaal')
			rows, fields = util.import_data(consult_f, delim=self.delim)
			consult_headers, self.num_cons, self.num_cons_pos = self.insert_data(
									rows, fields, 
									'icpc', 
									['datum', 'datum'], 
									'[A-Z][0-9][0-9]', 3,
									incorporate_SOEP='soepcode')
			headers = headers + consult_headers

		# gather data from referral csv
		if 'referrals' in needs_processing and needs_processing['referrals']:
			ref_f = util.select_file(files, 'verwijzing')
			rows, fields = util.import_data(ref_f, delim=self.delim)
			ref_headers,_,_ = self.insert_data(
									rows, fields, 
									'specialisme', 
									['datum', 'datum'], 
									'.*', None)
			headers = headers + ref_headers

		# gather data from comorbidity csv
		if 'comorbidity' in needs_processing and needs_processing['comorbidity']:
			comor_f = util.select_file(files, 'comorbiditeit')
			rows, fields = util.import_data(comor_f, delim=self.delim)
			comor_headers,_,_ = self.insert_data(
									rows, fields, 
									'omschrijving', 
									['begindatum', 'einddatum'],
									'.+', None,
									suffix='comorbiditeit')
			headers = headers + comor_headers

		# gather data from lab results csv
		if 'lab_results' in needs_processing and needs_processing['lab_results']:
			lab_f = util.select_file(files, 'bepaling')
			rows, fields = util.import_data(lab_f, delim=self.delim)
			lab_headers, self.num_lab, self.num_lab_pos = self.insert_data(
									rows, fields, 
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

	def get_IDs(self, rows, headers):
		'''sets all IDs as keys to a dict. Additionally adds gender/age data
			and date registration data'''

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

	def get_CRC_occurrences(self, rows, headers):
		'''sets all CRC cases to initial diagnosis date values in 
			id2data[patient][CRC_dates][0]'''

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

	# def generate_lab_attributes(self, original_code, suffix):
	# 	'''generates abstracted lab attributes, such as increasing HB, or low HB'''

	def generate_attributes(self, original_code, limit, suffix, src=''):
		'''Generate the attributes. In the most simple case
			this is a single attribute, namely the code + the 
			specified suffix.'''
		return [self.generate_code(original_code, limit) + '_' + suffix]

	def move_target_to_end_of_list(self):
		'''moves first data value to end of list for each instance in data dictionary'''
		for k in self.id2data:
			data = self.id2data[k]['data']
			data.append(data.pop(0))

	def make_lab_values(self, val, min_val, max_val):
		try:
			val = float(val.replace(',', '.'))
		except ValueError:
			val = ''
		try:
			min_val = float(min_val.replace(',', '.'))
		except ValueError:
			min_val = ''
		try:
			max_val = float(max_val.replace(',', '.'))
		except ValueError:
			max_val = ''
		return val, min_val, max_val

	def	save_output(self, benchmark=False, sequence_file=False, sub_dir='', name='unnamed', target=False):
		'''saves processed data to the specified output directory'''

		# if we didn't get the data from sql database, just save to .csv
		if not self.from_sql:

			# possibly make new directories
			out_dir = self.out_dir + '/' + sub_dir + '/'
			util.make_dir(out_dir)

			f_out = out_dir + name + '.csv'
			out = write_csv(f_out)
			
			# write headers where required
			if benchmark:
				out.writerow(self.headers[0:3])
			elif target:
				out.writerow([self.headers[0], self.headers[-1]])
			elif sequence_file:
				pass
			else:
				out.writerow([self.headers[0]] + self.headers[3:-1])

			# write data
			for value in self.id2data.values():
				data = value['data']
				if benchmark:
					data = data[0:3]
				elif target:
					data = [data[0], data[-1]]
				elif sequence_file:
					pass
				else:
					data = [data[0]] + data[3:-1]
				out.writerow(data)
		
		else: # if we DID get the data from the sql database, we also want to save it there (i.e. create new tables)
			tbl_name = 'AUTO_' + name
			cursor = util.sql_connect().cursor()

			if benchmark:
				try:
					init_query = 'CREATE TABLE {} ({} number(7), {} number(3), {} varchar2(10))'.format(tbl_name, headers[0], headers[1], headers[2])
					fill_query = sql.make_filling_query(tbl_name, 1, 3, self.id2data.values())

					# make table + columns
					sql.new_table(cursor, init_query, fill_query)
				except Exception, e:
					print e
			elif target:
				try:
					init_query = 'CREATE TABLE {} ({} number(7), {} varchar2(50))'.format(tbl_name, headers[0], headers[-1])
					fill_query = sql.make_filling_query(tbl_name, -1, None, self.id2data.values())

					# make table + columns
					sql.new_table(cursor, init_query, fill_query)
				except Exception, e:
					print e
			elif sequence_file:
				pass
			else:
				try:
					columns_str = ' NUMBER(3),'.join(self.headers[3:-1]) + ' NUMBER(3)'
					init_query = 'CREATE TABLE {} ({} number(7), {})'.format(tbl_name, headers[0], columns_str)
					
					fill_query = sql.make_filling_query(tbl_name, 3, -1, self.id2data.values())

					# make table + columns
					sql.new_table(cursor, init_query, fill_query)
				except Exception, e:
					print e				

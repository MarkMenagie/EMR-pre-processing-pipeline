from in_out import read_csv
import os
from datetime import datetime
import cx_Oracle

def import_data(f, delim=','):
	'''import data and separates the column names from the data'''
	rows = read_csv(f, delim=delim)
	headers = get_headers(rows.next())
	return rows, headers

def get_headers(row):
	'''returns the non-capitalised and bugfixed version of the header'''
	headers = [el.lower() for el in row]
	headers[0] = headers[0].split("\xef\xbb\xbf")[1] if headers[0].startswith('\xef') else headers[0] # fix funny encoding problem
	return headers

def select_file(files, s):
	'''returns the first file which contains the string s in the filename.
		if no such file is found, returns -1'''
	for f in files:
		if s in f.split('/')[-1]:
			return f
	return -1

def make_list_using_indices(row, indices):
	'''returns the sublist of row corresponding to all indices'''
	return [row[idx] for idx in indices]

def init_key(d, k, v):
	'''initialises a default value v for a non-existing key k in a dictionary d'''
	if not k in d:
		d[k] = v

def make_dir(s):
	'''creates the directory s if it does not exist'''
	if not os.path.exists(os.path.dirname(s)):
		os.makedirs(os.path.dirname(s)) 

def append_slash(s):
	'''appends a slash to the string if it does not end in one and returns it'''
	if not s[-1] == '/': 
		s = s + '/'
	return s

def list_dir_csv(s, skip_list=-1):
	'''returns a list of all csv's in a directory s, optionally skipping a file
		if one of a specified list of strings occurs in its filename'''
	result = [s + '/' + f for f in os.listdir(s) if f.endswith('.csv')]
	if skip_list != -1:
		result = [el for el in result if not occurs_in(el, skip_list)]
	return result

def occurs_in(s, lst):
	'''returns True if s occurs as a substring in the list of strings'''
	for el in lst:
		if el in s:
			return True
	return False

def get_current_datetime():
	'''returns the current datetime in a neat format'''
	now = datetime.now()
	d = str(now.date())
	t = str(now.time())[:-7]
	now = ('D' + d + '-T' + t).replace(':', '-')
	return now

def get_dict_val(dct, key, default=None):
	'''returns the value in dct[key]. If key is not in dct, returns default'''
	return dct[key] if key in dct else default

def tkinter2var(d):
	'''return a new dict with the tkinter variables converted to the actual humn-readable variables'''
	result = dict()
	for k in d:
		if type(d[k]) == dict:
			result[k] = tkinter2var(d[k])
		else:
			try:
				result[k] = d[k].get()
			except:
				print d[k]
				pass
	return result

def sql_connect():
	'''connects to the SQL database, returns server handle'''
	return cx_Oracle.connect('datamart', 'datamart', '10.67.201.10:1521/XE')



	
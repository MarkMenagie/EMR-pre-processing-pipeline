from in_out import read_csv
import os
from datetime import datetime

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
	'''returns the first file which contains the string s in the filename'''
	for f in files:
		if s in f.split('/')[-1]:
			return f

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

def list_dir_csv(s):
	'''returns a list of all csv's in a directory s'''
	return [s + '/' + f for f in os.listdir(s) if f.endswith('.csv')]

def get_current_datetime():
	'''returns the current datetime in a neat format'''
	now = datetime.now()
	d = str(now.date())
	t = str(now.time())[:-7]
	now = ('D' + d + '-T' + t).replace(':', '-')
	return now

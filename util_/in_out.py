import csv
import matplotlib.pyplot as plt
import numpy as np
from operator import itemgetter

def read_csv(f, delim=','):
	'''opens a csv reader object'''
	return csv.reader(open(f, 'rb'), delimiter=delim)

def write_csv(f):
	'''opens a csv writer object'''	
	return csv.writer(open(f,"wb"))

def iter_to_csv(iterator, f):
	'''writes the contents of a generator to a csv file'''
	out = write_csv(f)
	for row in iterator:
		out.writerow(row)

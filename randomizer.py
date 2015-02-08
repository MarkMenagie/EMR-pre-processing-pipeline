import numpy as np
import csv as csv
import random as random
import os
import sys

# return patient numbers not yet previously seen in other files (current_orig)
def get_new_patient_numbers(current_orig, filename, patientnumberfieldname, delim, check):
	rows = csv.reader(open(filename, "rb"), delimiter=delim)
	headers = [h.strip() for h in rows.next()]
	patient_num_idx = headers.index(patientnumberfieldname)
	
	new_orig = []
	cnt=0
	for row in rows:
		try:
			new_orig.append(row[patient_num_idx].strip())
		except IndexError:
			print row, len(row)
			cnt+=1
		except ValueError:
			print row, len(row)
			cnt+=1
	# print 'skipped', cnt, 'in file', filename

	# print len(new_orig), len(current_orig)
	# print len(set(new_orig)), len(set(current_orig))
	# print len(set(new_orig)- set(current_orig))
	return list(set(new_orig) - set(current_orig))

# create the mapping using all patient numbers we can find; 
# a patient needs to be present in at least a single table
# to be added to the mapping
def create_mapping(filenames, dirname, patientnumberfieldname, delim, offset, save_mapping, check=True):
	mapping_dir = dirname + "/meta-info/"
	if not os.path.exists(os.path.dirname(mapping_dir)):
		os.makedirs(os.path.dirname(mapping_dir)) 

	orig = []
	for filename in filenames:
		orig = orig + get_new_patient_numbers(orig, filename, patientnumberfieldname, delim, check)

	### randomization step ###
	# rand = list(orig)
	rand = range(int(offset), len(orig)+int(offset))
	random.shuffle(rand) 

	# perform some sanity checks - did we randomize okay?
	if check:
		print 'first five values of each array'
		print np.array(orig)[0:5]	
		print np.array(rand)[0:5]
		print 'checking values in orig'
		print len(orig), len(set(orig)), (len(orig) == len(set(orig)))
		print 'checking values in rand'
		print len(rand), len(set(rand)), (len(rand) == len(set(rand)))
		print max(orig), max(rand)


	# create the mapping which we'll use for all files so
	# we ensure changing each patient in each table with the same random identifier
	mapping = dict(zip(orig, rand))	# key=original patient number, val=new associated one
	out = csv.writer(open(mapping_dir + "info.csv","wb"))
	out.writerow(["smallest patient number", min(rand)])
	out.writerow(["largest patient number", max(rand)])
	
	if save_mapping:
		for key, value in mapping.iteritems():
			out.writerow([key, value])

	if len([i for i in range(len(orig)) if orig[i] == rand[i]]) != 0:
		print 'going at it again because there are ' + str(len([i for i in range(len(orig)) if orig[i] == rand[i]])) + ' non-changed patientnumber(s)'
		return create_mapping(filenames, patientnumberfieldname, delim, offset, save_mapping, check)
	return mapping

def replace_patient_numbers(filename, dirname, patientnumberfieldname, mapping, delim):
	rows = csv.reader(open(filename, "rb"), delimiter=delim)
	
	if not os.path.exists(os.path.dirname(dirname + "/randomized/")):
		os.makedirs(os.path.dirname(dirname + "/randomized/")) 

	out = csv.writer(open(dirname + "/randomized/" + filename.split('/')[-1],"wb"))

	headers = [h.strip() for h in rows.next()]
	out.writerow(headers)

	patient_num_idx = headers.index(patientnumberfieldname)
	cnt=0
	for row in rows:
		# if '400246413' in row[patient_num_idx]:
		# 	print row[patient_num_idx], mapping[row[patient_num_idx].strip()]
		try:
			row[patient_num_idx] = mapping[row[patient_num_idx].strip()]
			out.writerow(row)
		except IndexError:
			print row, len(row)
			cnt+=1
		except ValueError:
			print row, len(row)
			cnt+=1
	# print 'skipped', cnt, 'in file', filename, 'during replacement'
	return

if __name__ == "__main__":
	previous_file=[]
	if sys.argv[1:] != []:
		previous_file = sys.argv[1]

	data_dir = "non-random"
	filenames = [data_dir+'/'+f for f in os.listdir(data_dir) if f.endswith('.csv')]

	mapping = create_mapping(filenames, previous_file, True)

	for filename in filenames:
		replace_patient_numbers(filename, mapping)



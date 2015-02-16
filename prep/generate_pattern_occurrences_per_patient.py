import sys
from frequent_patterns import generate
import numpy as np

import util
import in_out
from StateInterval import new_SI
from StateSequence import StateSequence
from Pattern import Pattern


def generate_pattern_occurrences_per_patient(out_dir, sequence_file, min_sup):
	'''generates pattern, then checks for occurrences per patient and writes to csv'''
	# generate patterns
	patterns, p_pos, p_neg = generate(sequence_file, min_sup)

	# save patterns
	patterns2csv(patterns, sequence_file)

	# open writer
	out_f = out_dir + '/temporal.csv'
	out = in_out.write_csv(out_f)
	
	# open reader
	rows = in_out.read_csv(sequence_file)

	# make & write header
	header = ['patient','age','gender'] + ['p'+str(p) for p in range(len(patterns))] + ['CRC']
	out.writerow(header)

	# check for each pattern whether it matches in the patient (1) or not (0)
	for row in rows:
		write_record(row, out, patterns)

def patterns2csv(patterns, sequence_file):
	'''writes the patterns to a csv'''
	patterns = ([i] + p.__str__().split(',') for i, p in enumerate(patterns))
	f = sequence_file.split('sequences.csv')[0] + 'patterns.csv'
	in_out.iter_to_csv(patterns, f)

def write_record(record, out, patterns):
	'''writes each individual instance to csv'''
	SS = make_state_sequence(record)
	patient = SS.patient
	gender = SS.gender
	birthyear = SS.birthyear
	pattern_occurrences = [1 if (pattern.id_list and SS.patient in pattern.id_list) or SS.covered_by(pattern) else 0 for pattern in patterns]
	target = "negative" if SS.crc=='0' else "positive"
	out.writerow([patient, str(2011-int(birthyear)), gender] + pattern_occurrences + [target])

def make_state_sequence(record):
	'''recreates the state sequence used when mining for frequent patterns'''
	patient = record[0]
	birthyear = record[1]
	gender = record[2]
	patterns = record[3:-1]
	crc = record[-1]
	for i in range(len(patterns)):
		str_SI = patterns[i].split(';')
		patterns[i] = new_SI(str_SI[0], str_SI[1], str_SI[2])
	return StateSequence(patterns, patient, gender, birthyear, crc)

if __name__ == "__main__":
	args = sys.argv[1:]
	min_sup = float(args[1])
	save_patterns_per_patient(args[0], min_sup)

import sys
from collections import defaultdict
import numpy as np
from operator import itemgetter

import util_.in_out as in_out
from Pattern import Pattern, enrich_pattern
from StateInterval import StateInterval
from StateSequence import StateSequence

# mine all frequent patterns (> min_sup) in the specified file
def generate(sequence_file, min_sup, verbose=False):

	sequences = in_out.read_csv(sequence_file)
	sequences_pos = patients_with_class_val(sequences, 'positive')

	sequences = in_out.read_csv(sequence_file)
	sequences_neg = patients_with_class_val(sequences, 'negative')

	if verbose: 
		print "Patient dict:"
		print sequences_neg

	print '###### Mining positive CRC freq patterns ######'
	frequent_patterns_pos, MPTP_pos = mine(sequences_pos, min_sup, sequences_neg, verbose)
	print '###### Mining negative CRC freq patterns ######'
	frequent_patterns_neg, MPTP_neg = mine(sequences_neg, min_sup, sequences_pos, verbose)
	
	# print frequent_patterns_pos
	# print frequent_patterns_neg
	# save for later use !
	# MPTP_pos.update(MPTP_neg)
	# print len(list(set(frequent_patterns_pos+frequent_patterns_neg)))
	# print len(MPTP_pos)
	print '###### Done mining patterns ######'
	return list(set(frequent_patterns_pos+frequent_patterns_neg)), frequent_patterns_pos, frequent_patterns_neg

def patients_with_class_val(arr, class_val):
	result = {lst[0] : lst[1:-1] for lst in arr if lst[-1] == class_val}
	for k in result:
		record = result[k][2:]
		gender = result[k][1]
		birthyear = result[k][0]
		for i in range(len(record)):
			str_SI = record[i].split(';')
			record[i] = StateInterval(str_SI[0], str_SI[1], str_SI[2])
		result[k] = StateSequence(record, k, gender, birthyear)
	return result

# import cProfile, pstats
# Fx means Frequent x-patterns
def mine(data_dict, min_sup, negated_data, verbose):
	print("...generating 1-patterns"),
	F1 = generate_F1(data_dict, min_sup, negated_data)
	if verbose: print F1
	k_max = len(max(data_dict.values(), key=len)) if len(data_dict)!=0 else 0 # k = length of the longest instance, because that is how the maximum number of combinations possible for this specific group
	if verbose: print "longest patient sequence: " + str(k_max)
	
	F1 = set(F1.values())
	Fk = set(F1)
	MPTPs = set([p for p in F1 if p.is_significant(alpha=0.05)])
	candidates = list(F1)
	print "...found " + str(len(candidates))
	result = list(candidates)
	
	for k in range(0,k_max):
		print("...generating " + str(k+2) + '-patterns'),

		potential_Fk = generate_candidates(candidates, Fk, F1, min_sup, data_dict)
		Fk = evaluate_support(potential_Fk, data_dict, min_sup, negated_data, MPTPs)

		result = result + Fk
		print "...found " + str(len(Fk))
		if len(Fk) == 0:
			break
		# if k==2: exit()
	return result, MPTPs#[c for c in result if c.is_frequent]

def generate_F1(data_dict, min_sup, negated_data):
	len_data = len(data_dict)

	instances = [data_dict[sequence].get_states() for sequence in data_dict ]

	y_occurrences = defaultdict(int)
	for states in instances:
		for state in set(states): # for all unique states
			y_occurrences[state] += 1


	negated_instances = [negated_data[sequence].get_states() for sequence in negated_data ]
	all_occurrences = dict(y_occurrences)
	for states in negated_instances:
		for state in set(states): # for all unique states
			if state not in all_occurrences:
				all_occurrences[state] = 0
			all_occurrences[state] += 1

	# calc frequent patterns (more freq than min_sup)
	init_mcs = len_data / len_data + len(negated_data)
	# init_mc = len(data_dict) / (len(data_dict) + len(negated_data))

	F1=dict()
	for key in y_occurrences:
		states = np.array([key])
		relations = np.empty((1,1), dtype='S1')
		relations.fill(' ')
		loc_support = y_occurrences[key]/float(len_data)
		y_support = y_occurrences[key]/float(len_data+len(negated_data))
		all_support = all_occurrences[key]/float(len_data+len(negated_data))
		if loc_support >= min_sup:
			F1[key] = Pattern(states, relations, sup=loc_support, subpatterns=[], in_candidates=True)
			F1[key].generate_id_list(data_dict, False)
			F1[key].generate_id_list(negated_data, True)
			F1[key].is_frequent = (loc_support >= min_sup)
			# F1[key].mcs = init_mcs
			# F1[key].confidence = y_support/float(all_support)
			# F1[key].calc_max_conf()
	return F1

# for pseudocode, see "A Temporal Pattern Mining Approach for Classifying Electronics Health Record Data"
def generate_candidates(all_patterns, Fk, F1, min_sup, data_dict):
	len_data = float((len(data_dict)))

	candidates = []
	for k_pattern in Fk: # for all frequent k-patterns
		for singleton in F1: # for all singletons

			superpatterns, all_patterns = generate_coherent_superpatterns(k_pattern, singleton, data_dict, all_patterns) # generate new candidates

			for superpattern in superpatterns: # for each k+1-pattern created, we check if it is frequent
				subpatterns = superpattern.get_subpatterns()
	
				# intersection of all created subpatterns and all frequent k-patterns 
				frequent_subs = [pattern for pattern in Fk if pattern in subpatterns]

				# if the created subpatterns are all in Fk
				if len(frequent_subs) >= len(subpatterns):
					if len(frequent_subs) > len(subpatterns):
						print '> (impossible)'
					superpattern.generate_pid_list(frequent_subs)
					# superpattern.generate_pid_list(frequent_subs, negated=True)
					# superpattern.calc_max_conf_subpatterns(frequent_subs)
					if (len(superpattern.pid_list)/len_data) > min_sup:
						candidates.append(superpattern)
	return candidates

def evaluate_support(patterns, data, min_sup, negated_data, MPTPs):
	len_data = len(data)

	result = []
	p_values = []
	for p in patterns:
		p.generate_id_list(data, negated=False)
		p.calculate_support(min_sup, len_data)

		if p.support >= min_sup:
			result.append(p)

	return result

def generate_coherent_superpatterns(P, S, data_dict, all_patterns, strict_matching=True):
	superpatterns = []
	rel_length = P.relations.shape[1] + 1
	rels = np.empty((rel_length), dtype='S1')
	rels.fill('b')
	rels[0] = ' '

	new_p = enrich_pattern(P, S, rels, data_dict)
	if new_p not in all_patterns:
		superpatterns.append(new_p)
		all_patterns.append(new_p)

	if strict_matching:
		for i in range(1, len(rels)):
			rels[i] = 'c'
			new_p = enrich_pattern(P, S, rels, data_dict)
			if new_p not in all_patterns:
				superpatterns.append(new_p)
				all_patterns.append(new_p)

	return superpatterns, all_patterns

if __name__ == "__main__":
	args = sys.argv[1:]
	if len(args) != 1 and len(args) != 2:
		print "faulty input argument(s). try again"
		print "usage: python frequent_patterns.py path/to/state_sequences.py"
		print "and optinally, add a minimum support (default 0.1)"
		exit()
	if len(args) == 2:
		generate(args[0], min_sup=float(args[1]), verbose=False)
	elif len(args) == 1:
		generate(args[0], verbose=False)

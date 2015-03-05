from StandardProcess import StandardProcess
from SequenceProcess import SequenceProcess
import util_.util as util
import util_.in_out as io

class StandardEnrichProcess(StandardProcess):
	'''Class describing standard way of preprocessing the data by 
		counting occurrences of enriched data concepts. Here, 
		enrichment indicates an abstraction of the original
		data is used, such as using side effects instead of
		medication.'''

	def __init__(self, in_dir, delim, out_dir, ID_column, min_age, max_age, interval, mapping_files_dir):
		StandardProcess.__init__(self, in_dir, delim, out_dir, ID_column, min_age, max_age, interval)
		
		# dict of enrichment dicts which describe the transformation from a code to some abstraction
		self.code2x_dict = fill_enrichment_dicts(mapping_files_dir)

	def generate_attributes(self, code, limit, suffix, src=''):
		'''Generate the attributes. In the case of 
			StandardEnrichProcess, this is a collection of 
			side effects, indications, and active ingredients.'''
		return generate_enriched_attributes(code, limit, suffix, src, self.code2x_dict, self.__class__.__bases__[0], self)

class SequenceEnrichProcess(SequenceProcess):
	'''Class describing sequential/temporal way of preprocessing 
		the data by analyzing patterns of enriched data concepts
		Here, enrichment indicates an abstraction of the original
		data is used, such as using side effects instead of
		medication.'''

	def __init__(self, in_dir, delim, out_dir, ID_column, min_age, max_age, interval, mapping_files_dir):
		SequenceProcess.__init__(self, in_dir, delim, out_dir, ID_column, min_age, max_age, interval)
		
		# list of enrichments dicts which describe the transformation from a code to some abstraction
		self.code2x_dict = fill_enrichment_dicts(mapping_files_dir)

	def generate_attributes(self, code, limit, suffix, src=''):
		'''Generate the attributes. In the case of 
			SequenceEnrichProcess, this is a collection of 
			side effects, indications, and active ingredients.'''
		return generate_enriched_attributes(code, limit, suffix, src, self.code2x_dict, self.__class__.__bases__[0], self)

def generate_enriched_attributes(code, limit, suffix, src, code2, ParentClass, process_instance):
	'''Generate enriched attributes.'''
	# which source file are we currently investigating?
	if src == 'atc_code': 
		# get all medication enrichments, adding a suffix to each attribute identify the source
		effects = util.get_dict_val(code2['effects'], code, default=[])
		effects = [effect + '_side_effect' for effect in effects]

		indications = util.get_dict_val(code2['indications'], code, default=[])
		indications = [indication + '_indication' for indication in indications]

		ingredients = util.get_dict_val(code2['ingredients'], code, default=[])
		ingredients = [ingredient + '_ingredient' for ingredient in ingredients]

		return effects + indications + ingredients
	# elif src == 'icpc':
	 	# diagnosis enrichments
	# elif src == 'specialisme':
		# referral enrichments
	# elif src == 'omschrijving:'
		# comorbidity enrichments
	# elif src == 'code':
		# lab result enrichments
	else:
		# default enrichment (= none, just return original value + suffix)
		#print 'no known associated enrichment possible with source {}. Returning original value and continuing'.format(src)
		return ParentClass.generate_attributes(process_instance, code, limit, suffix, src) # 'super' class call

def fill_enrichment_dicts(mapping_files_dir):
	'''loads the enrichment mappings'''

	# initiate result as a dict of dicts
	result = dict()

	# read frequent effects, put effects in dict, put dict in result
	rows = io.read_csv(mapping_files_dir + '/atc/effects_frequent.csv')
	code2effects = {row[0] : row[1:] for row in rows}
	result['effects'] = code2effects

	# read frequent indications, put indications in dict, put dict in result
	rows = io.read_csv(mapping_files_dir + '/atc/indications_frequent.csv')
	code2indications = {row[0] : row[1:] for row in rows}
	result['indications'] = code2indications

	# read frequent ingredients, put ingredients in dict, put dict in result
	rows = io.read_csv(mapping_files_dir + '/atc/ingredients_frequent.csv')
	code2ingredients = {row[0] : row[1:] for row in rows}
	result['ingredients'] = code2ingredients

	return result


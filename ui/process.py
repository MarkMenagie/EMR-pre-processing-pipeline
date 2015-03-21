from datetime import datetime
import time

import util_.util as util
import util_.in_out as io

from prep.StandardProcess import StandardProcess
from prep.SequenceProcess import SequenceProcess
from prep.MarshallProcess import MarshallProcess
from prep.EnrichProcesses import StandardEnrichProcess, SequenceEnrichProcess
from prep.generate_pattern_occurrences_per_patient import generate_pattern_occurrences_per_patient

from Tab import PipelineTab
from Tkinter import LEFT, BooleanVar, DISABLED, W, E, NORMAL
from ttk import Label, Checkbutton, Radiobutton, Button
from context_sensitive.raw2attributes import Raw2Attributes
from context_sensitive.raw2patterns import Raw2Patterns

class ProcessTab(PipelineTab):

	def init_components(self):
		'''inits process frame's components (buttons, fields, labels, underlying methods)'''
		self.setup_IO_dirs()
		self.setup_general()
		self.setup_radio_buttons()
		self.setup_HIS_choice()
		self.setup_launcher()
		self.pack()

	def setup_IO_dirs(self):
		'''add I/O part'''
		dct = self.user_input

		dct['in_dir'] = self.button_component('Browse', 'input folder', 0, 0)
		dct['delimiter'] = self.general_component('Delimiter', 1, 0, init_val=',')
		dct['out_dir'] = self.button_component('Browse', 'output folder', 2, 0)

	def setup_general(self):
		'''add options part'''
		dct = self.user_input

		dct['min_age'] = self.general_component('Minimum age', 3, 0)
		dct['max_age'] = self.general_component('Maximum age', 4, 0)
		dct['begin_interval'] = self.general_component('First interval day', 5, 0, help_txt='')
		dct['end_interval'] = self.general_component('Last interval day', 6, 0, help_txt='')
		dct['ID_column'] = self.general_component('ID column name', 7, 0, init_val='patientnummer')

		enrich_val = BooleanVar()
		dct['enrich'] = enrich_val
		Checkbutton(self,text='semantic enrichment', variable=enrich_val).grid(row=8, column=0, columnspan=2, sticky=W)
		dct['mapping_dir'] = self.button_component('Browse', 'semantic enrichment dir', 9, 0)

		verbose_val = BooleanVar()
		dct['verbose'] = verbose_val
		Checkbutton(self,text='verbose (N/A)', variable=verbose_val, state=DISABLED).grid(row=10, column=0, columnspan=2, sticky=W)

	def setup_radio_buttons(self):
		'''add atemporal vs temporal choice part'''
		dct = self.user_input

		temporal_processing_flag = BooleanVar()

		# get context dependent frame (regular)
		regular = Raw2Attributes()
		regular_frame = regular.make_frame(self)
		reg_button = Radiobutton(self, text='raw2attributes', value=False, variable=temporal_processing_flag)
		reg_button.grid(row=11, column=0, sticky=W)

		# get context dependent frame (temporal)
		temporal = Raw2Patterns()
		temporal_frame = temporal.make_frame(self)
		tmprl_button = Radiobutton(self, text='raw2patterns', value=True, variable=temporal_processing_flag)
		tmprl_button.grid(row=11, column=1, sticky=W)

		# configure events, invoke one by default
		reg_button.configure(command=lambda : self.set_frame(regular_frame, temporal_frame))
		tmprl_button.configure(command=lambda : self.set_frame(temporal_frame, regular_frame))
		reg_button.invoke() # default
		
		dct['process_temporal'] = temporal_processing_flag
		dct['a-temporal_specific'] = regular.get_values()
		dct['temporal_specific'] = temporal.get_values()

	def set_frame(self, new_f, old_f):
		'''set the context dependent frame, initiated by a push on a radio button'''
		old_f.grid_forget()
		new_f.grid(row=12, column=0, rowspan=6, columnspan=2, sticky=W)

	def setup_HIS_choice(self):
		dct = self.user_input

		Label(self, text='HISes to consider (only when using SQL):').grid(row=18, column=0, columnspan=2, sticky=W)
		dct['PMO'] = self.checkbutton_component('Utrecht Promedico', 19, 0, init_val='PMO', onvalue='PMO', offvalue='')
		dct['MDM'] = self.checkbutton_component('Utrecht Medicom', 20, 0, init_val='MDM', onvalue='MDM', offvalue='')
		dct['LUMC'] = self.checkbutton_component('Leiden', 21, 0, init_val='LUMC', onvalue='LUMC', offvalue='')
		dct['VUMH'] = self.checkbutton_component('Amsterdam MicroHIS', 22, 0, init_val='VUMH', onvalue='VUMH', offvalue='')
		dct['VUMD'] = self.checkbutton_component('Amsterdam Medicom', 23, 0, init_val='VUMD', onvalue='VUMD', offvalue='')
		dct['VUSC'] = self.checkbutton_component('Amsterdam Scipio', 24, 0, init_val='VUSC', onvalue='VUSC', offvalue='')

	def defaults(self):
		'''set the user_input dict to default values'''
		dct = self.user_input

		dct['in_dir'].set('sql')
		dct['delimiter'].set(',')
		dct['out_dir'].set('./out')
		dct['min_age'].set(30)
		dct['max_age'].set(150)
		dct['begin_interval'].set(int(365./52*26+1))
		dct['end_interval'].set(int(365./52*0+1))
		dct['ID_column'].set('patientnummer')
		dct['temporal_specific']['support'].set(0.1)
		dct['mapping_dir'].set('../out/semantics/')

		dct['PMO'].set('PMO')
		dct['MDM'].set('MDM')
		dct['LUMC'].set('LUMC')
		dct['VUMH'].set('VUMH')
		dct['VUMD'].set('VUMD')
		dct['VUSC'].set('VUSC')

	def go(self, button):
		'''initiates the associated algorithms '''
		dct = self.user_input

		button.config(text='Running', state=DISABLED)
		if dct['in_dir'].get() == 'input folder':
			dct['in_dir'].set('sql')
		if dct['delimiter'].get() == '':
			dct['delimiter'].set(',')
		if dct['out_dir'].get() == 'output folder':
			dct['out_dir'].set('./out')
		if dct['min_age'].get() == '':
			dct['min_age'].set(30)
		if dct['max_age'].get() == '':
			dct['max_age'].set(150)
		if dct['begin_interval'].get() == '':
			dct['begin_interval'].set(int(365./52*26+1))
		if dct['end_interval'].get() == '':
			dct['end_interval'].set(int(365./52*0+1))
		if dct['ID_column'].get() == '':
			dct['ID_column'].set('patientnummer')
		if dct['temporal_specific']['support'].get() == '':
			dct['temporal_specific']['support'].set(0.1)
		if dct['mapping_dir'].get() == 'semantic enrichment dir':
			dct['mapping_dir'].set('../out/semantics_preliminary/')


		self.master.update_idletasks()

		now = util.get_current_datetime()
		util.make_dir(dct['out_dir'].get() + '/' + now + '/')

		HISes = [dct['PMO'].get(), dct['MDM'].get(), dct['LUMC'].get(), 
				 dct['VUMH'].get(), dct['VUMD'].get(), dct['VUSC'].get()]

		args = [dct['in_dir'].get(), 
				dct['delimiter'].get(),
				dct['out_dir'].get() + '/' + now, 
				dct['ID_column'].get(),
				int(dct['min_age'].get()),
				int(dct['max_age'].get()),
				[int(dct['end_interval'].get()), int(dct['begin_interval'].get())],
				True if dct['in_dir'].get().lower() == 'sql' else False,
				HISes]
		
		if dct['process_temporal'].get(): # process temporally
			self.temporal(dct, now, args)
		else: # process atemporally
			self.regular(dct, now, args)

		pretty_dct = util.tkinter2var(dct)
		try:
			io.pprint_to_file(dct['out_dir'].get() + '/' + now + '/settings.txt', pretty_dct)
		except IOError, e:
			print e

		print '### Done processing ###'
		button.config(text='Done')
		self.master.update_idletasks()
		time.sleep(0.5)	
		button.config(text='Run!', state=NORMAL)

	def temporal(self, dct, now, args):
		needs_processing = {k : bool(v.get()) for k, v in dct['temporal_specific'].iteritems()}

		out_dir = dct['out_dir'].get() + '/' + now + '/data/'
		util.make_dir(out_dir)
		min_sup = float(dct['temporal_specific']['support'].get())
		
		if not dct['temporal_specific']['sequences_available'].get():
			# if enrichment is enabled, we create a different object instance than usual
			if dct['enrich'].get():
				seq_p = SequenceEnrichProcess(*args, mapping_files_dir=dct['mapping_dir'].get())
				name = 'sequences_enriched'
			else:
				seq_p = SequenceProcess(*args)
				name = 'sequences'

			seq_p.process(needs_processing)
			seq_p.sort_sequences()
			seq_p.save_output(sequence_file=True, sub_dir='data/tmprl', name=name)

			generate_pattern_occurrences_per_patient(out_dir, seq_p.id2data, min_sup, dct['mapping_dir'].get())
			sequence_f = out_dir + '/tmprl/{}.csv'.format(name)
		else:
			sequence_f = dct['temporal_specific']['sequence_file'].get()
		# hier generaten met als extra input headers(?)/id2data
			generate_pattern_occurrences_per_patient(out_dir, sequence_f, min_sup, dct['mapping_dir'].get())

	def regular(self, dct, now, args):	
		needs_processing = {k : bool(v.get()) for k, v in dct['a-temporal_specific'].iteritems()}

		knowledge_driven = dct['a-temporal_specific']['knowledge-driven'].get()

		if knowledge_driven:
			std_p = MarshallProcess(*args)
			std_p.process(needs_processing)
			std_p.save_output(name='counts_knowledge_driven', sub_dir='data')			
		elif dct['enrich'].get():
			std_p = StandardEnrichProcess(*args, mapping_files_dir=dct['mapping_dir'].get())
			std_p.process(needs_processing)
			std_p.save_output(name='counts_enriched', sub_dir='data')
		else:
			std_p = StandardProcess(*args)
			std_p.process(needs_processing)
			std_p.save_output(name='counts', sub_dir='data')

		std_p.save_output(benchmark=True, sub_dir='data', name='age+gender')
		std_p.save_output(target=True, sub_dir='data', name='target')

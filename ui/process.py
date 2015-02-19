from datetime import datetime
import time

import util_.util as util

from prep.StandardProcess import StandardProcess
from prep.SequenceProcess import SequenceProcess
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
		self.setup_launcher()
		self.pack()

	def setup_IO_dirs(self):
		dct = self.user_input

		dct['in_dir'] = self.button_component('Browse', 'input folder', 0, 0)
		dct['delimiter'] = self.general_component('Delimiter', 1, 0, init_val=',')
		dct['out_dir'] = self.button_component('Browse', 'output folder', 2, 0)

	def setup_general(self):
		dct = self.user_input

		dct['min_age'] = self.general_component('Minimum age', 3, 0)
		dct['max_age'] = self.general_component('Maximum age', 4, 0)
		dct['begin_interval'] = self.general_component('First interval day', 5, 0, help_txt='')
		dct['end_interval'] = self.general_component('Last interval day', 6, 0, help_txt='')
		dct['ID_column'] = self.general_component('ID column name', 7, 0, init_val='patientnummer')

		verbose_val = BooleanVar()
		dct['verbose'] = verbose_val
		Checkbutton(self,text='verbose (N/A)', variable=verbose_val, state=DISABLED).grid(row=8, column=0, columnspan=2, sticky=W)

	def setup_radio_buttons(self):
		dct = self.user_input

		temporal_processing_flag = BooleanVar()

		# get context dependent frame (regular)
		regular = Raw2Attributes()
		regular_frame = regular.make_frame(self)
		reg_button = Radiobutton(self, text='raw2attributes', value=False, variable=temporal_processing_flag)
		reg_button.grid(row=9, column=0, sticky=W)

		# get context dependent frame (temporal)
		temporal = Raw2Patterns()
		temporal_frame = temporal.make_frame(self)
		tmprl_button = Radiobutton(self, text='raw2patterns', value=True, variable=temporal_processing_flag)
		tmprl_button.grid(row=9, column=1, sticky=W)

		# configure events, invoke one by default
		reg_button.configure(command=lambda : self.set_frame(regular_frame, temporal_frame))
		tmprl_button.configure(command=lambda : self.set_frame(temporal_frame, regular_frame))
		tmprl_button.invoke() # default
		
		dct['process_temporal'] = temporal_processing_flag
		dct['a-temporal_specific'] = regular.get_values()
		dct['temporal_specific'] = temporal.get_values()

	def set_frame(self, new_f, old_f):
		'''set the context dependent frame, initiated by a push on a radio button'''
		old_f.grid_forget()
		new_f.grid(row=10, column=0, rowspan=6, columnspan=2, sticky=W)

	def setup_launcher(self):
		'''create buttons to execute the job and for default values'''

		def_button = Button(self,text='Defaults')
		def_button.grid(row=16, column=0, padx=5, pady=5, sticky=W)
		def_button.configure(command=self.defaults)

		go_button = Button(self,text="Run!")
		go_button.grid(row=16, column=1, padx=5, pady=5, sticky=E)
		go_button.configure(command=lambda: self.go(go_button))

	def defaults(self):
		dct = self.user_input

		dct['in_dir'].set('/Users/Reiny/Documents/UI_CRC/playground')
		dct['delimiter'].set(',')
		dct['out_dir'].set('/Users/Reiny/Documents/UI_CRC/out')
		dct['min_age'].set(18)
		dct['max_age'].set(150)
		dct['begin_interval'].set(int(365./52*38))
		dct['end_interval'].set(int(365./52*12))
		dct['ID_column'].set('patientnummer')
		dct['temporal_specific']['support'].set(0.1)


	def go(self, button):
		dct = self.user_input

		button.config(text='Running', state=DISABLED)
		if dct['in_dir'].get() == 'input folder':
			dct['in_dir'].set('/Users/Reiny/Documents/UI_CRC/playground')
		if dct['delimiter'].get() == '':
			dct['delimiter'].set(',')
		if dct['out_dir'].get() == 'output folder':
			dct['out_dir'].set('/Users/Reiny/Documents/UI_CRC/out')
		if dct['min_age'].get() == '':
			dct['min_age'].set(18)
		if dct['max_age'].get() == '':
			dct['max_age'].set(150)
		if dct['begin_interval'].get() == '':
			dct['begin_interval'].set(int(365./52*38))
		if dct['end_interval'].get() == '':
			dct['end_interval'].set(int(365./52*12))
		if dct['ID_column'].get() == '':
			dct['ID_column'].set('patientnummer')
		if dct['temporal_specific']['support'].get() == '':
			dct['temporal_specific']['support'].set(0.1)

		self.master.update_idletasks()

		now = datetime.now()
		d = str(now.date())
		t = str(now.time())[:-7]
		now = ('D' + d + '-T' + t).replace(':', '-')
		util.make_dir(dct['out_dir'].get() + '/' + now)

		# process temporally
		if dct['process_temporal'].get():
			needs_processing = {k : bool(v.get()) for k, v in dct['temporal_specific'].iteritems()}

			out_dir = dct['out_dir'].get() + '/' + now + '/data/'
			util.make_dir(out_dir)
			min_sup = float(dct['temporal_specific']['support'].get())
			
			if not dct['temporal_specific']['sequences_available'].get():
				seq_p = SequenceProcess(dct['in_dir'].get(), 
						dct['delimiter'].get(),
						dct['out_dir'].get() + '/' + now, 
						dct['ID_column'].get(),
						int(dct['min_age'].get()),
						int(dct['max_age'].get()),
						[int(dct['end_interval'].get()), int(dct['begin_interval'].get())])
				
				seq_p.process(needs_processing)
				seq_p.save_output(include_headers=False, sub_dir='data/tmprl', name='sequences')

				sequence_f = out_dir + '/tmprl/sequences.csv'
			else:
				sequence_f = dct['temporal_specific']['sequence_file'].get()

			generate_pattern_occurrences_per_patient(out_dir, sequence_f, min_sup)

		# process atemporally
		else:
			needs_processing = {k : bool(v.get()) for k, v in dct['a-temporal_specific'].iteritems()}

			std_p = StandardProcess(dct['in_dir'].get(), 
					dct['delimiter'].get(),
					dct['out_dir'].get() + '/' + now, 
					dct['ID_column'].get(),
					int(dct['min_age'].get()),
					int(dct['max_age'].get()),
					[int(dct['end_interval'].get()), int(dct['begin_interval'].get())])
			
			std_p.process(needs_processing)
			std_p.save_output(name='counts', sub_dir='data')
			std_p.save_output(benchmark=True, sub_dir='data', name='benchmark')

		button.config(text='Done')
		self.master.update_idletasks()
		time.sleep(0.5)	
		# button.config(text='Wait')	
		# UI.update_idletasks()
		# time.sleep(0.5)	
		button.config(text='Run!', state=NORMAL)	


from Tkinter import Tk, W, E, N, S, StringVar, BooleanVar, Message, LEFT, DISABLED, NORMAL
from ttk import *
import tkFont
from tkFileDialog import askdirectory, askopenfilename
from os import listdir
import tkMessageBox
from datetime import datetime

import time
import prep.util as util
from prep.StandardProcess import StandardProcess
from prep.SequenceProcess import SequenceProcess
from prep.generate_pattern_occurrences_per_patient import generate_pattern_occurrences_per_patient
from ui.raw2attributes import Raw2Attributes
from ui.raw2patterns import Raw2Patterns

def init_UI(invoke=False):
	'''initializes the UI by creating tabs and the required content'''

	# initialize main window
	main = Tk()
	main.title('data2knowledge')

	# wrapper for 'tab' functionality
	n = Notebook(main)

	# add frames + content to notebook
	process_tab = Frame(n)
	fill_process_tab(process_tab)
	n.add(process_tab, text='Processing')

	learning_tab = Frame(n)
	fill_learning_tab(learning_tab)
	n.add(learning_tab, text='Learning')

	about_tab = Frame(n)
	fill_about_tab(about_tab)
	n.add(about_tab, text='About')

	# finish up, return UI
	n.pack()
	return main

def fill_process_tab(f):
	'''generates process frame's components (buttons, fields, labels, underlying methods)'''
	input_values = dict()

	setup_IO_dirs(f, input_values)
	setup_general(f, input_values)
	setup_radio_buttons(f, input_values)

	setup_launcher(f, input_values)

	f.pack()

def setup_IO_dirs(f, dct):
	dct['in_dir'] = button_component(f, 'Browse', 'input folder', 0, 0)
	dct['delimiter'] = general_component(f, 'Delimiter', 1, 0, init_val=',')
	dct['out_dir'] = button_component(f, 'Browse', 'output folder', 2, 0)

def button_component(f, button_txt, init_txt , r, c, help_txt=''):
	b = Button(f,text=button_txt)
	b.grid(row=r, column=c, sticky=W+E)
	dir_var = StringVar()
	dir_var.set(init_txt)
	Entry(f, textvariable=dir_var).grid(row=r, column=c+1)
	Label(f, text=help_txt).grid(row=r, column=c+2, sticky=W)
	b.configure(command=lambda: browse_dir(dir_var, b))
	return dir_var

def browse_dir(dir_var, button):
	s = askdirectory(parent=button)
	dir_var.set(s)

def setup_general(f, dct):
	dct['min_age'] = general_component(f, 'Minimum age', 3, 0)
	dct['max_age'] = general_component(f, 'Maximum age', 4, 0)
	dct['begin_interval'] = general_component(f, 'First interval day', 5, 0, help_txt='')
	dct['end_interval'] = general_component(f, 'Last interval day', 6, 0, help_txt='')
	dct['ID_column'] = general_component(f, 'ID column name', 7, 0, init_val='patientnummer')

	verbose_val = BooleanVar()
	dct['verbose'] = verbose_val
	Checkbutton(f, text='verbose (N/A)', variable=verbose_val, state=DISABLED).grid(row=8, column=0, columnspan=2, sticky=W)

def general_component(f, s, r, c, init_val='', help_txt=''):
	Label(f, text=s).grid(row=r, column=c, sticky=W)
	var = StringVar()
	var.set(init_val)
	Entry(f,textvariable=var).grid(row=r, column=c+1)	
	Label(f, text=help_txt).grid(row=r, column=c+2)
	return var		

def setup_radio_buttons(f, dct):
	temporal_processing_flag = BooleanVar()

	# get context dependent frame (regular)
	regular = Raw2Attributes()
	regular_frame = regular.make_frame(f)
	reg_button = Radiobutton(f, text='raw2attributes', value=False, variable=temporal_processing_flag)
	reg_button.grid(row=9, column=0, sticky=W)

	# get context dependent frame (temporal)
	temporal = Raw2Patterns()
	temporal_frame = temporal.make_frame(f)
	tmprl_button = Radiobutton(f, text='raw2patterns', value=True, variable=temporal_processing_flag)
	tmprl_button.grid(row=9, column=1, sticky=W)

	# configure events, invoke first one by default
	reg_button.configure(command=lambda : set_frame(regular_frame, temporal_frame))
	tmprl_button.configure(command=lambda : set_frame(temporal_frame, regular_frame))
	tmprl_button.invoke() # default
	
	dct['process_temporal'] = temporal_processing_flag
	dct['a-temporal_specific'] = regular.get_values()
	dct['temporal_specific'] = temporal.get_values()

def set_frame(new_f, old_f):
	'''set the context dependent frame, initiated by a push on a radio button'''
	old_f.grid_forget()
	new_f.grid(row=10, column=0, rowspan=6, columnspan=2, sticky=W)

def setup_launcher(f, dct):
	'''create buttons to execute the job and for default values'''
	def_button = Button(f,text='Defaults')
	def_button.grid(row=16, column=0, padx=5, pady=5, sticky=W)
	def_button.configure(command=lambda: defaults(dct))

	go_button = Button(f,text="Run!")
	go_button.grid(row=16, column=1, padx=5, pady=5, sticky=E)
	go_button.configure(command=lambda: go(dct, go_button))


def defaults(dct):
	dct['in_dir'].set('/Users/Reiny/Documents/UI_CRC/playground')
	dct['delimiter'].set(',')
	dct['out_dir'].set('/Users/Reiny/Documents/UI_CRC/out')
	dct['min_age'].set(18)
	dct['max_age'].set(150)
	dct['begin_interval'].set(int(365./52*38))
	dct['end_interval'].set(int(365./52*12))
	dct['ID_column'].set('patientnummer')
	dct['temporal_specific']['support'].set(0.1)


def go(dct, button):
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

	UI.update_idletasks()

	now = datetime.now()
	d = str(now.date())
	t = str(now.time())[:-7]
	now = ('D' + d + '-T' + t).replace(':', '-')
	util.make_dir(dct['out_dir'].get() + '/' + now)

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
	UI.update_idletasks()
	time.sleep(0.5)	
	button.config(text='Wait')	
	UI.update_idletasks()
	time.sleep(0.5)	
	button.config(text='Run!', state=NORMAL)	

def fill_learning_tab(f):
	'''generates learning frame's components (buttons, fields, labels, underlying methods)'''
	Label(f, text='Under construction.').grid()
	f.pack()

def fill_about_tab(f):
	'''generates about frame's components (label)'''
	disclaimer = '''This software may be used to anonymize datasets. Though it was tested and successfully used by myself, usage is at your own risk. For any questions, please contact me at r.kop@vu.nl.\n\n- Reinier Kop'''
	l = Message(f, justify=LEFT, text=disclaimer)
	l.grid()
	f.pack()

if __name__ == '__main__':
	UI = init_UI()
	UI.mainloop()
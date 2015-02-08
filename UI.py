from Tkinter import *
from ttk import *
from tkFileDialog import askdirectory, askopenfilename
from os import listdir
from randomizer import create_mapping, replace_patient_numbers
import tkMessageBox

from raw2attributes import Raw2Attributes
from raw2patterns import Raw2Patterns

def init_UI():
	'''initializes the UI by creating tabs and the required content'''

	# initialize main window
	main = Tk()
	main.title("data2knowledge")

	# wrapper for 'tab' functionality
	n = Notebook(main)

	# add frames + content to notebook
	process_tab = Frame(n)
	n.add(process_tab, text='Processing')
	fill_process_tab(process_tab)

	learning_tab = Frame(n)
	n.add(learning_tab, text='Learning')
	fill_learning_tab(learning_tab)

	about_tab = Frame(n)
	n.add(about_tab, text='About')
	fill_about_tab(about_tab)

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

def setup_IO_dirs(parent, dct):
	f = Frame(parent)
	dct['in_dir'] = browse_component(f, 'input folder...', 0, 0)
	dct['out_dir'] = browse_component(f, 'output folder...', 1, 0)
	f.grid(columnspan=2)

def browse_component(f, s, r, c):
	b = Button(f,text="Browse")
	b.grid(row=r, column=c, sticky=W)
	dir_var = StringVar()
	dir_var.set(s)
	Entry(f, textvariable=dir_var).grid(row=r, column=c+1)
	b.configure(command=lambda: browse_dir(dir_var, b))
	return dir_var

	def browse_dir(dir_var, button):
		s = askdirectory(parent=button)
		dir_var.set(s)

def setup_general(parent, dct):
	f = Frame(parent)

	dct['min_age'] = general_component(f, 'Minimum age', 0, 0)
	dct['max_age'] = general_component(f, 'Maximum age', 1, 0)
	dct['begin_interval'] = general_component(f, 'First interval day', 2, 0)
	dct['end_interval'] = general_component(f, 'Last interval day', 3, 0)

	f.grid(columnspan=2)

def general_component(f, s, r, c):
	Label(f, text=s).grid(row=r, column=c, sticky=W)
	var = StringVar()
	Entry(f,textvariable=var).grid(row=r, column=c+1)	
	return var		

def setup_radio_buttons(parent, dct):
	f = Frame(parent)

	temporal_processing_flag = BooleanVar()

	# get context dependent frame (regular)
	regular = Raw2Attributes()
	regular_frame = regular.get_frame(f)
	reg_button = Radiobutton(f, text='raw2attributes', value=False, variable=temporal_processing_flag)
	reg_button.grid(row=2, column=0, sticky=W)

	# get context dependent frame (temporal)
	temporal = Raw2Patterns()
	temporal_frame = temporal.get_frame(f)
	tmprl_button = Radiobutton(f, text='raw2patterns', value=True, variable=temporal_processing_flag)
	tmprl_button.grid(row=2, column=1, sticky=W)

	# configure events, invoke first one by default
	reg_button.configure(command=lambda : set_frame(regular_frame, temporal_frame))
	tmprl_button.configure(command=lambda : set_frame(temporal_frame, regular_frame))
	reg_button.invoke() # default
	
	dct['process_temporal'] = temporal_processing_flag
	dct['a-temporal_specific'] = regular.get_value_dict()
	dct['temporal_specific'] = temporal.get_value_dict()

	f.grid(columnspan=2)

def set_frame(new_f, old_f):
	'''set the context dependent frame, initiated by a push on a radio button'''
	old_f.grid_forget()
	new_f.grid(row=3, column=0, rowspan=5, columnspan=5)

def setup_launcher(f, dct):
	'''create buttons to execute the job and for default values'''
	def_button = Button(f,text='Defaults')
	def_button.grid(row=10, column=0, padx=5, pady=5, sticky=W)
	def_button.configure(command=lambda: defaults(dct))

	go_button = Button(f,text="Go!")
	go_button.grid(row=10, column=1, padx=5, pady=5, sticky=E)
	go_button.configure(command=lambda: go(dct))

def defaults(dct):
	dct['in_dir'].set('data/')
	dct['out_dir'].set('out/')
	dct['min_age'].set(18)
	dct['max_age'].set(150)
	dct['begin_interval'].set(int(365./52*38))
	dct['end_interval'].set(int(365./52*12))

def go(dct):
	if dct['min_age'].get() == '':
		dct['min_age'].set(18)
	if dct['max_age'].get() == '':
		dct['max_age'].set(150)
	if dct['begin_interval'].get() == '':
		dct['begin_interval'].set(int(365./52*38))
	if dct['end_interval'].get() == '':
		dct['end_interval'].set(int(365./52*12))

	from pprint import pprint
	pprint({k : (v.get() if type(v) != dict else {k : w for k, w in v.iteritems()}) for k, v in dct.iteritems()})

	if dct['process_temporal']:
		# state sequences.py

		# save TPs.py
		print
	else:
		# create.py
		print

def fill_learning_tab(f):
	'''generates learning frame's components (buttons, fields, labels, underlying methods)'''


def fill_about_tab(f):
	'''generates about frame's components (label)'''
	disclaimer = '''This software may be used to anonymize datasets. Though it was tested and successfully used by myself, usage is at your own risk. For any questions, please contact me at r.kop@vu.nl.\n\n- Reinier Kop'''
	Message(f, justify=LEFT, text=disclaimer).grid()

if False:
	Label(master, text="Column name").grid(row=1, column=0, sticky=W)
	fieldname = StringVar()
	fieldname.set('patientnummer')
	Entry(master,textvariable=fieldname).grid(row=1, column=1)			
	Message(master, width=500, justify=LEFT, text="2. Type the name of the column containing the identifier").grid(row=1,column=2, sticky=W)

	saveName = IntVar()
	Checkbutton(master, text="Save old --> new mapping?", variable=saveName).grid(row=4, column=0, columnspan=2, sticky=W)
	Message(master, width=500, justify=LEFT, text="5. Check to save (in directory meta-info/)").grid(row=4,column=2, sticky=W)

	Message(master, width=500, justify=LEFT, text="6. Press button; popup appears when complete (may take a couple of minutes)").grid(row=5,column=2, sticky=W)

if __name__ == '__main__':
	UI = init_UI()
	UI.mainloop()
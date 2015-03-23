import time

import util_.util as util
import util_.in_out as io

from reporting.Report import Report

from Tab import PipelineTab
from Tkinter import LEFT, BooleanVar, DISABLED, W, E, NORMAL, StringVar
from ttk import Label, Checkbutton, Radiobutton, Button, Entry
import tkFileDialog

class ReportTab(PipelineTab):

	def init_components(self):
		'''inits process frame's components (buttons, fields, labels, underlying methods)'''
		self.setup_IO_dirs()
		self.setup_general()
		self.setup_launcher()
		self.pack()

	def setup_IO_dirs(self):
		'''add I/O part'''
		dct = self.user_input

		Label(self, text='CSV with the ROC and confusion matrix:').grid(row=0, column=0, columnspan=2, sticky=W)
		dct['f_general'] = self.add_file_browser(self, 'Browse', '', 1, 0)
		Label(self, text='CSV with the predictors + importances:').grid(row=2, column=0, columnspan=2, sticky=W)
		dct['f_predictors'] = self.add_file_browser(self, 'Browse', '', 3, 0)
		Label(self, text='CSV with the corresponding data:').grid(row=4, column=0, columnspan=2, sticky=W)
		dct['f_data'] = self.add_file_browser(self, 'Browse', '', 5, 0)
		Label(self, text='CSV to write to:').grid(row=6, column=0, columnspan=2, sticky=W)
		dct['f_out'] = self.add_file_browser(self, 'Browse', '', 7, 0)
		dct['delimiter'] = self.general_component('Delimiter', 8, 0, init_val=',')

	def add_file_browser(self, f, button_txt, init_txt , r, c, help_txt=''):
		b = Button(f,text=button_txt)
		b.grid(row=r, column=c, sticky=W+E)
		f_var = StringVar()
		f_var.set(init_txt)
		e = Entry(f, textvariable=f_var)
		e.grid(row=r, column=c+1)
		b.configure(command=lambda: self.browse_file(f_var, b))
		return f_var

	def browse_file(self, dir_var, button):
		s = tkFileDialog.askopenfilename(parent=button)
		dir_var.set(s)

	def setup_general(self):
		'''add options part'''
		dct = self.user_input

		Label(self, text='').grid(row=9, column=0, columnspan=2)
		dct['feature-threshold'] = self.general_component('Feature threshold', 10, 0)

	def defaults(self):
		'''set the user_input dict to default values'''
		dct = self.user_input

		dct['f_general'].set('./out/out/newest/RF/temporal.csv')
		dct['f_predictors'].set('./out/out/newest/RF/features_temporal.csv')
		dct['f_data'].set('./out/combined/temporal.csv')
		dct['f_out'].set('./out/analysis/temporal_RF.csv')
		dct['feature-threshold'].set(0.1)

	def go(self, button):
		'''initiates the associated algorithms '''
		dct = self.user_input

		button.config(text='Running', state=DISABLED)

		self.master.update_idletasks()

		util.make_dir(dct['f_out'].get())

		report = Report(dct['f_general'].get(),
						dct['f_data'].get(),
						dct['f_predictors'].get(),
						dct['f_out'].get(),
						float(dct['feature-threshold'].get())
			)
		report.compile()
		report.export()

		print '### Done processing ###'
		button.config(text='Done')
		self.master.update_idletasks()
		time.sleep(0.5)	
		button.config(text='Run!', state=NORMAL)



from Tab import PipelineTab
from Tkinter import LEFT, BooleanVar, W, NORMAL, DISABLED
from ttk import Label, Checkbutton
from learn import learn
import time
import util_.util as util

class LearningTab(PipelineTab):

	def __init__(self, parent, title, master):
		'''initialize object'''
		self.buttons = dict()
		PipelineTab.__init__(self, parent, title, master)

	def init_components(self):
		'''inits learning frame's components (buttons, fields, labels, underlying methods)'''

		dct = self.user_input

		# I/O components
		dct['in_dir'] = self.button_component('Browse', 'input folder', 0, 0)
		dct['out_dir'] = self.button_component('Browse', 'output folder', 1, 0)

		# input the record and target id (e.g. 'patientnummer' and 'crc')
		dct['record_id'] = self.general_component('ID column name', 2, 0)

		# checkboxes allowing for algorithm selection
		self.DT, self.DT_btn = self.make_checkbutton(self, 'CART', 3, 0)
		self.user_input['DT'] = self.DT
		self.buttons['DT'] = self.DT_btn

		self.LR, self.LR_btn = self.make_checkbutton(self, 'LR', 4, 0)
		self.user_input['LR'] = self.LR
		self.buttons['LR'] = self.LR_btn

		self.RF, self.RF_btn = self.make_checkbutton(self, 'RF (100 Trees)', 5, 0)
		self.user_input['RF'] = self.RF
		self.buttons['RF'] = self.RF_btn

		self.RF, self.RF_btn = self.make_checkbutton(self, 'RF (10 Trees)', 6, 0)
		self.user_input['RFsmall'] = self.RF
		self.buttons['RFsmall'] = self.RF_btn

		self.SVM, self.SVM_btn = self.make_checkbutton(self, 'SVM', 7, 0)
		self.user_input['SVM'] = self.SVM
		self.buttons['SVM'] = self.SVM_btn

		Label(self, text='   ').grid(row=8, column=0, columnspan=2)
		
		self.FS, self.FS_btn = self.make_checkbutton(self, 'apply feature selection', 8, 0)
		self.user_input['FS'] = self.FS
		self.buttons['FS'] = self.FS_btn

		Label(self, text='   ').grid(row=9, column=0, columnspan=2)
		Label(self, text='If you want a separate testset, fill this in.').grid(row=10, column=0, columnspan=2, sticky=W)

		dct['in_dir2'] = self.button_component('Browse', 'input folder', 11, 0)

		self.sep_test, self.sep_test_btn = self.make_checkbutton(self, 'separate testset', 12, 0)
		self.user_input['sep_test'] = self.sep_test
		self.buttons['sep_test'] = self.sep_test_btn

		# setup algorithm launcher button (incl defaults button)
		self.setup_launcher()

		# compile
		self.pack()

	def make_checkbutton(self, f, s, r, c):
		v = BooleanVar()
		ch = Checkbutton(f, text=s, variable=v)
		ch.grid(row=r, column=c, columnspan=2, sticky=W)
		return v, ch

	def defaults(self):
		'''set the user_input dict to default values'''
		dct = self.user_input

		dct['in_dir'].set('./out/combined')
		dct['out_dir'].set('./out')
		dct['record_id'].set('ID')
		dct['DT'].set(True)
		dct['LR'].set(True)
		dct['RF'].set(False)
		dct['RFsmall'].set(False)
		dct['SVM'].set(False)
		dct['FS'].set(True)

		dct['in_dir2'].set('./out/combined')

	def go(self, button):
		'''initiates the associated algorithms '''
		button.config(text='Running', state=DISABLED)
		self.master.update_idletasks()

		dct = self.user_input
		
		in_dir = dct['in_dir'].get()

		now = util.get_current_datetime()
		out_dir = dct['out_dir'].get() + '/' + now
		
		algorithms = []
		if dct['DT'].get(): algorithms.append('DT')
		if dct['LR'].get(): algorithms.append('LR')
		if dct['RF'].get(): algorithms.append('RF')
		if dct['RFsmall'].get(): algorithms.append('RFsmall')
		if dct['SVM'].get(): algorithms.append('SVM')

		record_id = dct['record_id'].get().lower()
		target_id = 'target'
		feature_selection = dct['FS'].get()

		separate_testset = dct['sep_test'].get()
		in_dir2 = dct['in_dir2'].get()

		learn.execute(in_dir, out_dir, record_id, target_id, algorithms, feature_selection, separate_testset, in_dir2)

		button.config(text='Done')
		self.master.update_idletasks()
		time.sleep(0.5)	
		button.config(text='Run!', state=NORMAL)	

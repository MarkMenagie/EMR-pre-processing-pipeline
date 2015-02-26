from Tab import PipelineTab
from Tkinter import LEFT, BooleanVar, W, NORMAL, DISABLED
from ttk import Label, Checkbutton
from learn import learn
from time import time
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

		self.RF, self.RF_btn = self.make_checkbutton(self, 'RF', 5, 0)
		self.user_input['RF'] = self.RF
		self.buttons['RF'] = self.RF_btn

		self.SVM, self.SVM_btn = self.make_checkbutton(self, 'SVM', 6, 0)
		self.user_input['SVM'] = self.SVM
		self.buttons['SVM'] = self.SVM_btn

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

		dct['in_dir'].set('specify input directory!')
		dct['out_dir'].set('/Users/Reiny/Documents/UI_CRC/out')
		dct['record_id'].set('ID')
		dct['DT'].set(True)
		dct['LR'].set(True)
		dct['RF'].set(True)
		dct['SVM'].set(True)

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
		if dct['SVM'].get(): algorithms.append('SVM')

		record_id = dct['record_id'].get().lower()
		target_id = 'target'
		# target_id = dct['target_id'].get()

		learn.execute(in_dir, out_dir, record_id, target_id, algorithms)

		button.config(text='Done')
		self.master.update_idletasks()
		time.sleep(0.5)	
		button.config(text='Run!', state=NORMAL)	

import time
import util_.util as util
from Tab import PipelineTab
from Tkinter import DISABLED, NORMAL, StringVar, Radiobutton, W
import features.merge as combine
import features.extract as extract

class MergeTab(PipelineTab):

	def init_components(self):
		'''inits merge frame's components (buttons, fields, labels, underlying methods)'''
		self.setup_IO_dirs()
		self.setup_general()
		# self.setup_radio_buttons()
		self.setup_launcher()
		self.pack()

	def setup_IO_dirs(self):
		'''add I/O part'''
		dct = self.user_input

		dct['in_dir'] = self.button_component('Browse', 'input folder', 0, 0)
		dct['delimiter'] = self.general_component('Delimiter', 1, 0, init_val=',')
		dct['out_dir'] = self.button_component('Browse', 'output folder', 2, 0)
		dct['output_id'] = self.general_component('Output Name', 3, 0)

	def setup_general(self):
		'''add options part'''
		dct = self.user_input
		
		dct['age+gender'] = self.checkbutton_component('age+gender', 4, 0)
		dct['counts_med'] = self.checkbutton_component('counts (medication)', 5, 0)
		dct['counts_med_enrich'] = self.checkbutton_component('counts (medication enriched)', 6, 0)
		dct['counts_consult'] = self.checkbutton_component('counts (consults)', 7, 0)
		dct['counts_referral'] = self.checkbutton_component('counts (referrals)', 8, 0)
		dct['counts_lab'] = self.checkbutton_component('counts (lab)', 9, 0)
		# dct['enriched_counts'] = self.checkbutton_component('enriched counts', 6, 0)
		dct['tmprl'] = self.checkbutton_component('temporal (excl. enriched meds)', 10, 0)
		dct['enriched_tmprl'] = self.checkbutton_component('temporal (incl. enriched meds)', 11, 0)
		# dct['enriched_tmprl'] = self.checkbutton_component('enriched patterns', 8, 0)
		dct['target'] = self.checkbutton_component('target', 12, 0, init_val=True, mode=DISABLED)
	
	def setup_radio_buttons(self):
		'''add feature selection choice part'''
		dct = self.user_input

		selection_var = StringVar()
		# selection_var.set(0)

		# get context dependent frame (regular)
		no_selection_btn = Radiobutton(self, text='no feature selection', value='none', variable=selection_var)
		no_selection_btn.grid(row=13, column=0, columnspan=2, sticky=W)

		# get context dependent frame (temporal)
		pre_selection_btn = Radiobutton(self, text='pre-merge selection', value='pre', variable=selection_var)
		pre_selection_btn.grid(row=14, column=0, columnspan=2, sticky=W)

		# get context dependent frame (temporal)
		post_selection_btn = Radiobutton(self, text='post-merge selection', value='post', variable=selection_var)
		post_selection_btn.grid(row=15, column=0, columnspan=2, sticky=W)

		# configure events, invoke one by default
		no_selection_btn.invoke() # default
		
		dct['feature_selection'] = selection_var

	def defaults(self):
		'''set the user_input dict to default values'''
		dct = self.user_input

		dct['in_dir'].set('specify input directory!')
		dct['delimiter'].set(',')
		dct['out_dir'].set('/Users/Reiny/Documents/UI_CRC/out')
		dct['output_id'].set('counts')
		dct['age+gender'].set(True)
		dct['counts_med'].set(True)
		dct['counts_med_enrich'].set(False)
		dct['counts_consult'].set(True)
		dct['counts_referral'].set(True)
		dct['counts_lab'].set(True)
		dct['tmprl'].set(False)
		dct['enriched_tmprl'].set(False)

	def go(self, button):
		'''initiates the associated algorithms '''
		dct = self.user_input

		button.config(text='Running', state=DISABLED)
		if dct['in_dir'].get() == 'input folder':
			dct['in_dir'].set('/Users/Reiny/Documents/UI_CRC/playground')
		if dct['delimiter'].get() == '':
			dct['delimiter'].set(',')
		if dct['out_dir'].get() == 'output folder':
			dct['out_dir'].set('/Users/Reiny/Documents/UI_CRC/out')

		self.master.update_idletasks()

		now = util.get_current_datetime()
		util.make_dir(dct['out_dir'].get() + '/' + now)

		args = [dct['in_dir'].get(), 
				dct['delimiter'].get(),
				dct['out_dir'].get() + '/' + now + '/' + dct['output_id'].get() + '.csv', 
				dct['age+gender'].get(), 
				dct['counts_med'].get(), 
				dct['counts_med_enrich'].get(), 
				dct['counts_consult'].get(), 
				dct['counts_referral'].get(), 
				dct['counts_lab'].get(),
				dct['tmprl'].get(), 
				dct['enriched_tmprl'].get()
		]

		feature_selection = 'none'#dct['feature_selection'].get()

		# if pre-merge selection, perform feature selection
		if feature_selection == 'pre':
			extract.features(*args)
			dct['in_dir'].set(dct['in_dir'].get() + '/selected')

		# merge
		combine.execute(*args)

		# if post-merge selection, perform feature selection
		if feature_selection == 'post':
			dct['in_dir'].set(dct['out_dir'].get())
			dct['out_dir'].set(dct['out_dir'].get() + '/selected')
			extract.features(*args)

		button.config(text='Done')
		self.master.update_idletasks()
		time.sleep(0.5)	
		button.config(text='Run!', state=NORMAL)


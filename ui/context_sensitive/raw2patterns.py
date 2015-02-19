from raw2processed import Raw2Processed
from Tkinter import *
import tkFileDialog
from ttk import *

class Raw2Patterns(Raw2Processed):

	def make_frame(self, parent):
		f = Frame(parent)
		
		self.knowledge, self.knowledge_btn = self.make_checkbutton(f, 'knowledge driven only (N/A)', 0, 0)
		self.values['knowledge-driven'] = self.knowledge
		self.buttons['knowledge-driven'] = self.knowledge_btn
		self.knowledge_btn.configure(command=lambda : self.toggle_other_buttons('knowledge-driven'), state=DISABLED)

		self.medication, self.medication_btn = self.make_checkbutton(f, 'include medication', 1, 0)
		self.values['medication'] = self.medication
		self.buttons['medication'] = self.medication_btn
		# self.medication_btn.configure(command=lambda : self.no_knowledge(self.medication))

		self.consults, self.consults_btn = self.make_checkbutton(f, 'include consults', 2, 0)
		self.values['consults'] = self.consults
		self.buttons['consults'] = self.consults_btn
		# self.consults_btn.configure(command=lambda : self.no_knowledge(self.consults))

		self.referrals, self.referrals_btn = self.make_checkbutton(f, 'include referrals', 3, 0)
		self.values['referrals'] = self.referrals
		self.buttons['referrals'] = self.referrals_btn
		# self.referrals_btn.configure(command=lambda : self.no_knowledge(self.referrals))

		self.comorbidity, self.comorbidity_btn = self.make_checkbutton(f, 'include comorbidity', 4, 0)
		self.values['comorbidity'] = self.comorbidity
		self.buttons['comorbidity'] = self.comorbidity_btn
		# self.comorbidity_btn.configure(command=lambda : self.no_knowledge(self.comorbidity))

		self.lab_results, self.lab_results_btn = self.make_checkbutton(f, 'include lab results (N/A)', 5, 0)
		self.values['lab_results'] = self.lab_results
		self.buttons['lab_results'] = self.lab_results_btn
		# self.lab_results_btn.configure(command=lambda : self.no_knowledge(self.lab_results))
		self.lab_results_btn.configure(state=DISABLED)

		self.support_val, self.support = self.make_label(f, 'Min. support', 6, 0)
		self.values['support'] = self.support_val
		# self.buttons['lab_results'] = self.lab_results_btn
		# self.lab_results_btn.configure(command=lambda : self.no_knowledge(self.lab_results))

		self.patterns, self.patterns_btn = self.make_checkbutton(f, 'I already have the sequences', 7, 0)
		self.values['sequences_available'] = self.patterns
		self.buttons['sequences_available'] = self.patterns_btn
		self.patterns_btn.configure(command=lambda : self.sequence_mode(f, 'sequences_available'))

		self.add_file_browser(f, 'Browse', '', 8, 0)

		return f

	def sequence_mode(self, f, button_key):
		self.toggle_other_buttons(button_key)

		enabled = self.values[button_key].get()
		if enabled:
			for w in self.sequence_widgets:
				w.config(state=NORMAL)
		else:
			for w in self.sequence_widgets:
				w.config(state=DISABLED)

	def add_file_browser(self, f, button_txt, init_txt , r, c, help_txt=''):
		b = Button(f,text=button_txt)
		b.grid(row=r, column=c, sticky=W+E)
		f_var = StringVar()
		f_var.set(init_txt)
		e = Entry(f, textvariable=f_var)
		e.grid(row=r, column=c+1)
		b.configure(command=lambda: self.browse_file(f_var, b))

		self.sequence_widgets = [b, e]
		self.values['sequence_file'] = f_var

	def browse_file(self, dir_var, button):
		s = tkFileDialog.askopenfilename(parent=button)
		dir_var.set(s)



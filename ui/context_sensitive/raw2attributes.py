from raw2processed import Raw2Processed
from Tkinter import *
from ttk import *

class Raw2Attributes(Raw2Processed):

	def make_frame(self, parent):
		f = Frame(parent)
		
		self.knowledge, self.knowledge_btn = self.make_checkbutton(f, 'knowledge driven only (N/A)', 0, 0)
		self.values['knowledge-driven'] = self.knowledge
		self.buttons['knowledge-driven'] = self.knowledge_btn
		self.knowledge_btn.configure(command=self.knowledge_only, state=DISABLED)

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

		self.lab_results, self.lab_results_btn = self.make_checkbutton(f, 'include lab results', 5, 0)
		self.values['lab_results'] = self.lab_results
		self.buttons['lab_results'] = self.lab_results_btn
		# self.lab_results_btn.configure(command=lambda : self.no_knowledge(self.lab_results))

		return f
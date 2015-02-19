from Tkinter import W, E, StringVar
from ttk import Frame, Entry, Label, Button
from tkFileDialog import askdirectory, askopenfilename

class Tab(Frame):
	
	def __init__(self, parent, title, master):
		'''sets self to Frame with parent parent, initializes visuals and interactions, adds tab to parent notebook'''
		Frame.__init__(self, parent)
		self.master = master
		self.init_components()
		self.add_to(parent, title)

	def init_components(self):
		'''abstract method to be implemented by the derived class'''

	def add_to(self,parent, title):
		'''add self to parent with title title'''
		parent.add(self, text=title)

class PipelineTab(Tab):
	
	def __init__(self, parent, title, master):
		'''initialize object'''
		self.user_input = dict()
		Tab.__init__(self, parent, title, master)

	### methods which add often occurring combinations of interface components using the grid layout ###

	def button_component(self, button_txt, init_txt, r, c, help_txt=''):
		'''adds a button component associated with an entry (the label only activates when help_txt != '')'''
		b = Button(self, text=button_txt)
		b.grid(row=r, column=c, sticky=W+E)
		dir_var = StringVar()
		dir_var.set(init_txt)
		Entry(self, textvariable=dir_var).grid(row=r, column=c+1)
		Label(self, text=help_txt).grid(row=r, column=c+2, sticky=W)
		b.configure(command=lambda: self.browse_dir(dir_var, b))
		return dir_var

	def browse_dir(self, dir_var, button):
		'''called to browse a directory'''
		s = askdirectory(parent=button)
		dir_var.set(s)

	def general_component(self, s, r, c, init_val='', help_txt=''):
		'''adds a label, plus an entry and its associated variable'''
		Label(self, text=s).grid(row=r, column=c, sticky=W)
		var = StringVar()
		var.set(init_val)
		Entry(self, textvariable=var).grid(row=r, column=c+1)	
		Label(self, text=help_txt).grid(row=r, column=c+2)
		return var		


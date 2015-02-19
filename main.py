from Tkinter import Tk
from ttk import Notebook
from ui import ProcessTab, LearningTab, AboutTab

def init_UI():
	'''create tabs and required content'''

	# initialize main window
	main = Tk()
	main.title('data2knowledge')

	# component for 'tab' functionality
	n = Notebook(main)

	# initialize the various tabs
	ProcessTab(n, 'Process', main)
	LearningTab(n, 'Learn', main)
	AboutTab(n, 'About', main)

	# finish up, return UI
	n.pack()
	return main

if __name__ == '__main__':
	'''initialize GUI and start it'''
	gui = init_UI()
	gui.mainloop()
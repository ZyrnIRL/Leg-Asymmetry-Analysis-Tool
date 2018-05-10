import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from functools import partial
import copy

import filemanagement, datamanagement, analysis, serverinterface

# Define function to import external files when using PyInstaller.
def resourcePath(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		#base_path = sys._MEIPASS
		base_path = os.path.join(sys._MEIPASS, '..')
	except Exception:
		base_path = os.path.abspath(".")
	
	return os.path.join(base_path, relative_path)

qtCreatorFile = resourcePath("userinterface.ui")
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
 
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
	
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)
		self.setupUi(self)
		
		self.leftData = None
		self.rightData = None
		
		self.leftFiltered = None
		self.rightFiltered = None
		
		self.Graph1 = None
		self.Graph2 = None
		
		analysis.initializePlots(self)
		
		self.update()
		self.server()
		
		self.pushButton_Add.clicked.connect(lambda: self.addFile())
		self.pushButton_Left.clicked.connect(lambda: self.populate(self.tableWidget_Left, True))
		self.pushButton_Right.clicked.connect(lambda: self.populate(self.tableWidget_Right, False))
		self.pushButton_Delete.clicked.connect(lambda: self.delete())
		self.pushButton_Link.clicked.connect(lambda: self.makeLink())
		self.pushButton_Unlink.clicked.connect(lambda: self.removeLink())
		self.pushButton_Analyze.clicked.connect(lambda: self.analysis())
		self.pushButton_Creds.clicked.connect(lambda: self.openCred())
		self.pushButton_Connect.clicked.connect(lambda: self.connect())
		self.pushButton_Local.clicked.connect(lambda: self.local())
		self.pushButton_Server.clicked.connect(lambda: self.backup())
		self.pushButton_ClearLeft.clicked.connect(lambda: self.clear(True, False))
		self.pushButton_ClearRight.clicked.connect(lambda: self.clear(False, True))
		self.pushButton_ClearBoth.clicked.connect(lambda: self.clear(True, True))
		self.pushButton_Filter.clicked.connect(lambda: self.filter())
		
		self.lineEdit_Creds.textChanged.connect(lambda: self.typing())
	
	def clear(self, left, right):
		if left:
			self.tableWidget_Left.clearContents()
			self.tableWidget_Left.setEnabled(False)
			self.leftData = None
		if right:
			self.tableWidget_Right.clearContents()
			self.tableWidget_Right.setEnabled(False)
			self.rightData = None
		if self.rightData is None and self.leftData is None:
			self.pushButton_Analyze.setEnabled(False)
	
	def filter(self):
		selected = self.selectedID()
		if not len(selected) is 1:
			popup = QtWidgets.QMessageBox()
			popup.setText('Please select exactly one file for toggling filtering.')
			popup.setStandardButtons(QtWidgets.QMessageBox.Ok)
			popup.exec_()
		else:
			status = not filemanagement.getFiltered(selected[0])
			filemanagement.setFiltered(selected[0], status)
			self.update()
	
	def local(self):
		selected = self.selectedID()
		if not len(selected) is 1:
			popup = QtWidgets.QMessageBox()
			popup.setText('Please select exactly one file for download.')
			popup.setStandardButtons(QtWidgets.QMessageBox.Ok)
			popup.exec_()
		else:
			status = not filemanagement.getLocal(selected[0])
			filemanagement.setLocal(selected[0], status, self)
			self.update()
	
	def backup(self):
		selected = self.selectedID()
		if not len(selected) is 1:
			popup = QtWidgets.QMessageBox()
			popup.setText('Please select exactly one file for backup.')
			popup.setStandardButtons(QtWidgets.QMessageBox.Ok)
			popup.exec_()
		else:
			status = not filemanagement.getBackup(selected[0])
			filemanagement.setBackup(selected[0], status, self)
			self.update()
	
	def typing(self):
		if len(self.lineEdit_Creds.text()) == 0:
			self.pushButton_Connect.setEnabled(False)
		else:
			self.pushButton_Connect.setEnabled(True)
	
	def update(self):
		filemanagement.update(self.tableWidget_Manager)
	
	def server(self):
		serverinterface.update(self)
	
	def connect(self):
		serverinterface.setCredentials(self)
	
	def openCred(self):
		serverinterface.openCredentials(self)
		self.pushButton_Connect.setEnabled(True)
	
	def populate(self, table, leftSide):
		selected = self.selectedID()
		try:
			if not len(selected) is 1:
				raise Exception('Please select exactly one file for loading.\nLinked files will be loaded together.')
			elif leftSide:
				if not filemanagement.getLocal(selected[0]):
					raise Exception('The file you are trying to load is not local.\nPlease download the file first.')
				self.leftData = datamanagement.populateTable(table, filemanagement.fileFromID(selected[0]))
				self.leftFiltered = filemanagement.getFiltered(selected[0])
				self.pushButton_Analyze.setEnabled(True)
				data, filtered = self.populateLinked(self.tableWidget_Right, selected[0])
				if not data is None:
					self.rightData = data
					self.rightFiltered = filtered
			else:
				if not filemanagement.getLocal(selected[0]):
					raise Exception('The file you are trying to load is not local.\nPlease download the file first.')
				self.rightData = datamanagement.populateTable(table, filemanagement.fileFromID(selected[0]))
				self.rightFiltered = filemanagement.getFiltered(selected[0])
				self.pushButton_Analyze.setEnabled(True)
				data, filtered = self.populateLinked(self.tableWidget_Left, selected[0])
				if not data is None:
					self.leftData = data
					self.leftFiltered = filtered
		except Exception as e:
			popup = QtWidgets.QMessageBox()
			popup.setText(str(e))
			popup.setStandardButtons(QtWidgets.QMessageBox.Ok)
			popup.exec_()

	def populateLinked(self, table, id):
		link = filemanagement.getLink(id)
		if not link is None:
			filtered = filemanagement.getFiltered(link)
			if not filemanagement.getLocal(link):
				raise Exception('A linked file you are trying to load is not local.\nPlease download the file first.\nThe original file was still loaded.')
			return datamanagement.populateTable(table, filemanagement.fileFromID(link)), filtered
		else:
			return None, None
	
	def selectedID(self):
		selected = []
		rows = self.tableWidget_Manager.selectionModel().selectedRows()
		for item in rows:
			selected.append(item.row())
		#return self.tableWidget_Manager.currentRow()
		return selected
	
	def addFile(self):
		filemanagement.addFile()
		self.update()
	
	def delete(self):
		selected = self.selectedID()
		if not len(selected) is 1:
			popup = QtWidgets.QMessageBox()
			popup.setText('Please select exactly one file for deletion.')
			popup.setStandardButtons(QtWidgets.QMessageBox.Ok)
			popup.exec_()
		else:
			filemanagement.deleteFile(selected[0], self)
			self.update()
	
	def makeLink(self):
		selected = self.selectedID()
		if not len(selected) is 2:
			popup = QtWidgets.QMessageBox()
			popup.setText('Please select exactly two files for linking.')
			popup.setStandardButtons(QtWidgets.QMessageBox.Ok)
			popup.exec_()
		else:
			filemanagement.makeLink(selected[0], selected[1])
			self.update()
	
	def removeLink(self):
		selected = self.selectedID()
		if not len(selected) is 1:
			popup = QtWidgets.QMessageBox()
			popup.setText('Please select exactly one file for link removal.')
			popup.setStandardButtons(QtWidgets.QMessageBox.Ok)
			popup.exec_()
		else:
			filemanagement.removeLink(selected[0])
			self.update()
	
	def analysis(self):
		analysis.clearPlots(self)
		analysis.analyze(self)
		#self.progressBar_Analysis.setValue(1)
		#self.plot(self.leftData, self.leftGraph)
		#self.progressBar_Analysis.setValue(50)
		#analysis.variables(self.leftData)
		#self.progressBar_Analysis.setValue(100)
	
	#def plot(self, data, graph):
	#	graph.plot(data)

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = MyApp()
	window.show()
	sys.exit(app.exec_())
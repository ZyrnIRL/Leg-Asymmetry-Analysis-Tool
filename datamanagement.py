from PyQt5 import QtCore, QtWidgets

"""
WORKS

"""
def createEntry(table, row, col, data):
	entry = QtWidgets.QTableWidgetItem(data)
	if row == 0:
		entry.setFlags(QtCore.Qt.ItemIsEnabled)
	else:
		entry.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
	table.setItem(row, col, entry)

"""
WORKS

"""	
def populateTable(table, filename):
	try:
		array = []
		with open(filename) as file:
			dataset = file.readlines()
			table.setRowCount(len(dataset))
			row = 0
			for line in dataset:
				line = line.strip().split(',')
				array.append(line)
				if row == 0:
					table.setColumnCount(len(line))
				col = 0
				for data in line:
					createEntry(table, row, col, data)
					col += 1
				row += 1
		table.setEnabled(True)
		return array
	except Exception as e:
		popup = QtWidgets.QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QtWidgets.QMessageBox.Ok)
		popup.exec_()
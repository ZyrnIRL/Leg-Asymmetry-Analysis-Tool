import sys
import os
from os.path import isdir, isfile, getmtime
from time import localtime
from shutil import copy
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import serverinterface, datamanagement

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

managerFile = resourcePath('manage.txt')
dataPath = resourcePath('datasets')
firstLine = 'timestamp,accel_x (m/s2),accel_y (m/s2),accel_z (m/s2),gyro_x (deg/s),gyro_y (deg/s),gyro_z (deg/s),mag_x (uT),mag_y (uT),mag_z (uT)\n'
managerHeader = 'id,name,date,link,filtered,local,backup\n'

labels = managerHeader.strip().split(',')
nameIndex = labels.index('name')
linkIndex = labels.index('link')
filteredIndex = labels.index('filtered')
localIndex = labels.index('local')
backupIndex = labels.index('backup')

"""
WORKS

"""
def update(table):
	createDatabase()
	createManager()
	datamanagement.populateTable(table, managerFile)

"""
Create the database directory if it doesn't already exist.
This directory stores all local dataset files.
"""
def createDatabase():
	try:
		if not isdir(dataPath):
			os.mkdir(dataPath)
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()

"""
Create the dataset management file if it doesn't already exist.
This file stores information about all managed files.
"""
def createManager():
	try:
		if not isfile(managerFile):
			with open(managerFile, 'w+') as file:
				file.write(managerHeader)
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()

"""
Opens a file selection popup to begin managing a file.
Only allows files with the first line header specific to IMU devices.
Does not allow duplicate filenames, they should be renamed before adding again.
Places a copy of the file in the database directory and information within the management file.
"""
def addFile():
	fileName = QFileDialog.getOpenFileName()[0]
	if not isDuplicate(fileName):
		try:
			with open(fileName) as file:
				if file.readline() == firstLine:
					copy(fileName, dataPath)
					addManager(fileName)
				else:
					popup = QMessageBox()
					popup.setText('Not correct file format.')
					popup.setStandardButtons(QMessageBox.Ok)
					popup.exec_()
		except Exception as e:
			popup = QMessageBox()
			popup.setText(str(e))
			popup.setStandardButtons(QMessageBox.Ok)
			popup.exec_()
	else:
		popup = QMessageBox()
		popup.setText('Filename already exists in database.')
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()

"""
Checks to see if a filename already exists within the management file.
Will work as long as 'name' is an attribute in the header.
Returns a boolean for the outcome.
"""
def isDuplicate(fileName):
	name = fileName.split('/')[-1]
	nameIndex = managerHeader.strip().split(',').index('name')
	try:
		with open(managerFile, 'r') as file:
			for line in file:
				if line.strip().split(',')[nameIndex] == name:
					return True
			return False
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()

"""
Adds information on the dataset to the management file.
ID is determined by number of entries already being managed.
Initially set with no linked file and only a local backup.
"""
def addManager(fileName):
	try:
		with open(managerFile, 'a+') as file:
			file.seek(0)
			id = len(file.readlines())
			name = fileName.split('/')[-1]
			date = localtime(getmtime(fileName))
			date = '{}-{}-{}'.format(date.tm_year, date.tm_mon, date.tm_mday)
			file.write('{},{},{},None,False,True,False\n'.format(id, name, date))
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()

"""
UNTESTED
Changes the status of the local backup of a file.
Takes a boolean as the status and either downloads or deletes the file.
Does not allow deletion if there is no backup.
"""
def setLocal(id, status, app):
	try:
		with open(managerFile, 'r') as file:
			lines = file.readlines()
		info = lines[id].strip().split(',')
		name = info[nameIndex]
		fileName = dataPath + '/' + name
		
		if status:
			serverinterface.downloadFile(name, fileName, app)
			#with open(fileName, 'w+') as file:
			#	file.write(dataset)
		else:
			if not getBackup(id):
				raise Exception('Please backup the file before removing locally.')
			os.remove(fileName)
		
		info[localIndex] = str(status)
		lines[id] = ','.join(info) + '\n'
		with open(managerFile, 'w') as file:
			for line in lines:
				file.write(line)
		
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()

"""
UNTESTED
Changes the status of the server backup of a file.
Takes a boolean as the status and either uploads or deletes the file.
"""
def setBackup(id, status, app):
	try:
		with open(managerFile, 'r') as file:
			lines = file.readlines()
		info = lines[id].strip().split(',')
		name = info[nameIndex]
		fileName = dataPath + '/' + name
		
		if status:
			#with open(fileName, 'r') as file:
			#	dataset = file.readlines()
			serverinterface.uploadFile(fileName, name, app)
		else:
			if not getLocal(id):
				raise Exception('Please download the file before removing backup.')
			serverinterface.removeFile(name, app)
		
		info[backupIndex] = str(status)
		lines[id] = ','.join(info) + '\n'
		with open(managerFile, 'w') as file:
			for line in lines:
				file.write(line)
		
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()

"""
WORKS

"""
def makeLink(id1, id2):
	try:
		removeLink(id1)
		removeLink(id2)
		
		with open(managerFile, 'r') as file:
			lines = file.readlines()
		info1 = lines[id1].strip().split(',')
		info2 = lines[id2].strip().split(',')
		
		info1[linkIndex] = str(id2)
		info2[linkIndex] = str(id1)
		
		lines[id1] = ','.join(info1) + '\n'
		lines[id2] = ','.join(info2) + '\n'
		
		with open(managerFile, 'w') as file:
			for line in lines:
				file.write(line)
		
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()

"""
WORKS

"""
def getLink(id):
	try:
		with open(managerFile, 'r') as file:
			lines = file.readlines()
		
		info = lines[id].strip().split(',')
		link = info[linkIndex]
		
		if link == 'None':
			return None
		else:
			return int(link)
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()
		return None

"""
UNTESTED

"""
def getLocal(id):
	try:
		with open(managerFile, 'r') as file:
			lines = file.readlines()
		
		info = lines[id].strip().split(',')
		status = info[localIndex]
		if status == 'True':
			return True
		else:		
			return False
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()
		return None

"""
UNTESTED

"""
def getBackup(id):
	try:
		with open(managerFile, 'r') as file:
			lines = file.readlines()
		
		info = lines[id].strip().split(',')
		status = info[backupIndex]
		if status == 'True':
			return True
		else:		
			return False
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()
		return None

"""
WORKS

"""
def removeLink(id):
	try:
		with open(managerFile, 'r') as file:
			lines = file.readlines()
		
		info1 = lines[id].strip().split(',')
		link = info1[linkIndex]
		
		if not link == 'None':
			info2 = lines[int(link)].strip().split(',')
			info2[linkIndex] = 'None'
			lines[int(link)] = ','.join(info2) + '\n'
		
		info1[linkIndex] = 'None'
		lines[id] = ','.join(info1) + '\n'
		
		with open(managerFile, 'w') as file:
			for line in lines:
				file.write(line)
		
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()
	

"""
Removes a file from being managed.
Gets rid of the local dataset along with the backed up version.
Decrements the IDs of all following files.
Updates link information.
"""
def deleteFile(id, app):
	try:
		with open(managerFile, 'r') as file:
			lines = file.readlines()
		
		info = lines.pop(id).strip().split(',')
		name = info[nameIndex]
		local = getLocal(id)
		backup = getBackup(id)
		
		if backup:
			if not app.widget_Backup.isEnabled():
				raise Exception('Please connect to the server before deleting a backed up file.')
		
		for i in range(id, len(lines)):
			line = lines[i].split(',')
			line[0] = str(int(line[0]) - 1)
			lines[i] = ','.join(line)
		lines = fixLinks(id, lines)
		
		if local:
			os.remove(dataPath + '/' + name)
		if backup:
			serverinterface.removeFile(name, app)
		
		with open(managerFile, 'w') as file:
			for line in lines:
				file.write(line)
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()

"""
Fixes the links between files after a file is deleted.
Files linked to the deleted ID have links replaced with None.
Files linked to IDs that were decremented have links updated.
"""
def fixLinks(id, lines):
	fixed = []
	for line in lines:
		line = line.split(',')
		if not (line[linkIndex] == 'link' or line[linkIndex] == 'None'):
			if int(line[linkIndex]) == id:
				line[linkIndex] = 'None'
			elif int(line[linkIndex]) > id:
				line[linkIndex] = str(int(line[linkIndex]) - 1)
		fixed.append(','.join(line))
	return fixed
	
def fileFromID(id):
	try:
		with open(managerFile, 'r') as file:
			lines = file.readlines()
		info = lines[id].strip().split(',')
		name = info[nameIndex]
		fileName = dataPath + '/' + name
		return fileName
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()

def getFiltered(id):
	try:
		with open(managerFile, 'r') as file:
			lines = file.readlines()
		
		info = lines[id].strip().split(',')
		status = info[filteredIndex]
		if status == 'True':
			return True
		else:		
			return False
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()
		return None

def setFiltered(id, status):
	try:
		with open(managerFile, 'r') as file:
			lines = file.readlines()
		info = lines[id].strip().split(',')
		info[filteredIndex] = str(status)
		lines[id] = ','.join(info) + '\n'
		with open(managerFile, 'w') as file:
			for line in lines:
				file.write(line)
		
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()
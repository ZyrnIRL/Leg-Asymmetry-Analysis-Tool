from google.cloud import storage
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from os.path import isfile
import sys
import os
import random

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

defaultBucket = 'imu-data-analysis'
serverFile = resourcePath('server.txt')

def update(app):
	createServer()
	try:
		with open(serverFile, 'r') as file:
			info = file.readlines()
			if info[0].strip() == 'DISABLE':
				app.tab_Settings.setEnabled(False)
				return
			creds = info[0].strip()
			if not creds == 'None':
				app.lineEdit_Creds.setText(creds)
				app.pushButton_Connect.setEnabled(True)
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()

def openCredentials(app):
	fileName = QFileDialog.getOpenFileName()[0]
	try:
		app.lineEdit_Creds.setText(fileName)
	except Exception as e:
			popup = QMessageBox()
			popup.setText(str(e))
			popup.setStandardButtons(QMessageBox.Ok)
			popup.exec_()

def setCredentials(app):
	try:
		if app.checkBox_Creds.isChecked():
			creds = app.lineEdit_Creds.text()
		else:
			creds = 'None'
		with open(serverFile, 'r') as file:
			data = file.readlines()
		data[0] = creds + '\n'
		with open(serverFile, 'w') as file:
			file.writelines(data)
		createBucket(app)
		
		app.widget_Backup.setEnabled(True)
		
		popup = QMessageBox()
		popup.setText('Connected successfully.')
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()

def createBucket(app):
	storage_client = createClient(app)
	if storage_client.lookup_bucket(getBucket()) is None:
		try:
			create_bucket(getBucket(), app)
		except:
			bucket = getBucket() + random.randint(0, 1000000)
			create_bucket(bucket, app)
			setBucket(bucket)

def setBucket(bucket):
	try:
		with open(serverFile, 'r') as file:
			data = file.readlines()
		data[0] = bucket
		with open(serverFile, 'w') as file:
			file.writelines(data)
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()

def createServer():
	try:
		if not isfile(serverFile):
			with open(serverFile, 'w+') as file:
				file.write('None\n' + defaultBucket)
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()

def getBucket():
	try:
		with open(serverFile, 'r') as file:
			bucket = file.readlines()[1].strip()
		return bucket
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()

def getCredentials(app):
	try:
		with open(serverFile, 'r') as file:
			credentials = file.readlines()[0].strip()
		if credentials == 'None':
			credentials = app.lineEdit_Creds.text()
		return credentials
	except Exception as e:
		popup = QMessageBox()
		popup.setText(str(e))
		popup.setStandardButtons(QMessageBox.Ok)
		popup.exec_()

def uploadFile(fileName, name, app):
	upload_blob(getBucket(), fileName, name, app)

def removeFile(name, app):
	delete_blob(getBucket(), name, app)

def downloadFile(name, fileName, app):
	download_blob(getBucket(), name, fileName, app)

def createClient(app):
	return storage.Client.from_service_account_json(getCredentials(app))

def create_bucket(bucket_name, app):
    """Creates a new bucket."""
    storage_client = createClient(app)
    bucket = storage_client.create_bucket(bucket_name)
    print('Bucket {} created'.format(bucket.name))

def upload_blob(bucket_name, source_file_name, destination_blob_name, app):
    """Uploads a file to the bucket."""
    storage_client = createClient(app)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))
		
def download_blob(bucket_name, source_blob_name, destination_file_name, app):
    """Downloads a blob from the bucket."""
    storage_client = createClient(app)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print('Blob {} downloaded to {}.'.format(
        source_blob_name,
        destination_file_name))

def delete_blob(bucket_name, blob_name, app):
    """Deletes a blob from the bucket."""
    storage_client = createClient(app)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.delete()

    print('Blob {} deleted.'.format(blob_name))
from PyInstaller.utils.hooks import copy_metadata
datas = copy_metadata('google-cloud')
datas += copy_metadata('google-api-core')
datas += copy_metadata('google-cloud-core')
# Leg-Asymmetry-Analysis-Tool
## How to run
Either run main.py or download and unzip the latest release version.  
The latest release is a frozen executable along with all required files.  
The only files not included are the Google credentials and any datasets.  

## Dependencies when running just Python
pip install google-cloud-storage

Anaconda  
OR  
pip install PyQt5  
pip install numpy
pip install scipy  
pip install matplotlib  
Probably some others I'm forgetting about  

## How to freeze
pip install pyinstaller  

The following command line code works for me but could vary by user.  
pyinstaller --hidden-import scipy._lib.messagestream --paths "C:\ProgramData\Anaconda3\Lib\site-packages\scipy\extra-dll" --additional-hooks-dir=hooks main.py  

This should be called after navigating to the source folder.  
"C:\ProgramData\Anaconda3\Lib\site-packages\scipy\extra-dll" should be the extra-dll folder under the scipy installation.  
This could vary but should be this location if Anaconda is installed.  
The hooks directory is included and allows the Google API to be found.

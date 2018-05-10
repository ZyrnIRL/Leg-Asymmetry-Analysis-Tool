# Leg-Asymmetry-Analysis-Tool
## How to run
Either run main.py or download and unzip the latest release version.  
The latest release is a frozen executable along with all required files.  
The only files not included are the Google credentials and any datasets.

## File organization
After running a folder named datasets and two text files named manage and server are created.  
If running the frozen binary, these will be created one folder level above so they can be easily found and not accidentally deleted.  
It is recommended to create a shortcut to the executable in the same area, again for easy access.  
Everything in the source folder of the zip was created by PyInstaller and contains all modules for running the code.  
If using just the Python code, each file contains their respective functions and are called from the main file.

## Special settings
The backup options can be disabled by including "DISABLE" as the first line of the server text file.

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
pyinstaller --noconsole --hidden-import scipy._lib.messagestream --paths "C:\ProgramData\Anaconda3\Lib\site-packages\scipy\extra-dll" --additional-hooks-dir=hooks main.py

This should be called after navigating to the source folder.  
"C:\ProgramData\Anaconda3\Lib\site-packages\scipy\extra-dll" should be the extra-dll folder under the scipy installation.  
This could vary but should be this location if Anaconda is installed.  
The hooks directory is included and allows the Google API to be found.

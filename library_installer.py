import os
import sys
import subprocess

filename = 'requirements.txt'
path = os.path.isfile(filename)
print("Make sure your library_install.py and requirements.txt are under the same directory.")

try:
    subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
except subprocess.CalledProcessError:
    print("pip is not installed or not accessible.")
    print("Please install pip first: https://pip.pypa.io/en/stable/installation/")
    sys.exit(1)

if path:
    print("Preparing install libraries")
    os.system(f'pip install -r {filename}')
    print("Installation completed")
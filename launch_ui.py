# launch_streamlit.py

import os
import sys
from pathlib import Path

# Add outerfolder to the Python path
sys.path.append(str(Path(__file__).resolve().parent))    
print(list(sys.path))

# Import and run the Streamlit app
import subprocess

# Adjust the path to your Streamlit script as needed
streamlit_script_path = "ui\Register.py"
subprocess.run(["streamlit", "run", streamlit_script_path])

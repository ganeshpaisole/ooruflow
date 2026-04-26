"""
OoruFlow — Run this to scaffold the full project (web + mobile + docker).
    python setup_project.py
"""
import subprocess, sys
subprocess.run([sys.executable, "setup_files.py"], check=True)

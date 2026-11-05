# Executive Streamlit Launcher script
import os
import subprocess
import sys
from pathlib import Path


def main():
    root_dir = Path(__file__).resolve().parent
    os.chdir(root_dir)
    cmd = [sys.executable, "-m", "streamlit", "run", "app_streamlit.py", "--server.port", "8501"]
    print("Launching AUTONOMO CFO Streamlit App...")
    subprocess.run(cmd, check=False)

if __name__ == "__main__":
    main()

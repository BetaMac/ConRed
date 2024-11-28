import PyInstaller.__main__
import sys
from pathlib import Path

# Get the current directory
current_dir = Path(__file__).parent

# Add any additional files or folders that need to be included
additional_files = []

PyInstaller.__main__.run([
    str(current_dir / 'conred_gui.py'),  # Full path to your main GUI script
    '--name=ConRed',
    '--onefile',
    '--windowed',
    f'--add-data={str(current_dir / "conred.py")};.',  # Include your original ConRed class
    *additional_files
])
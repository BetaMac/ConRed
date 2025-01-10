import PyInstaller.__main__
import sys
from pathlib import Path
import os
import shutil

# Get the current directory
current_dir = Path(__file__).parent

# Create necessary directories
output_dir = Path('data/output')
output_dir.mkdir(parents=True, exist_ok=True)

# Create the correct --add-data arguments format for your platform
def get_add_data_arg(source, dest):
    # Use semicolon on Windows, colon on other platforms
    separator = ';' if sys.platform.startswith('win') else ':'
    return f'--add-data={source}{separator}{dest}'

# Clean up previous build
dist_dir = Path('dist')
build_dir = Path('build')
if dist_dir.exists():
    shutil.rmtree(dist_dir)
if build_dir.exists():
    shutil.rmtree(build_dir)

# Create the PyInstaller command
args = [
    str(current_dir / 'conred_gui.py'),  # Main script
    '--name=ConRed',
    '--onefile',
    '--windowed',
    '--clean',
    '--hidden-import=mammoth',
    '--hidden-import=docx',
    '--hidden-import=lxml',
    '--collect-all=mammoth',
    '--collect-all=docx',
    '--collect-all=lxml',
    get_add_data_arg(str(current_dir / 'conred.py'), '.'),
    get_add_data_arg(str(current_dir / 'markdown_converter.py'), '.'),
    get_add_data_arg('config.json', '.'),
    get_add_data_arg('data', 'data'),  # Include entire data directory
]

# Run PyInstaller
PyInstaller.__main__.run(args)

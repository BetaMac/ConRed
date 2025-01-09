import PyInstaller.__main__
import sys
from pathlib import Path

# Get the current directory
current_dir = Path(__file__).parent

# Create the correct --add-data arguments format for your platform
def get_add_data_arg(source, dest):
    # Use semicolon on Windows, colon on other platforms
    separator = ';' if sys.platform.startswith('win') else ':'
    return f'--add-data={source}{separator}{dest}'

# Create the PyInstaller command
args = [
    str(current_dir / 'conred_gui.py'),  # Main script
    '--name=ConRed',
    '--onefile',
    '--windowed',
    get_add_data_arg(str(current_dir / 'conred.py'), '.'),
    get_add_data_arg('config.json', '.'),
    get_add_data_arg('data/input/*.xml', 'data/input')
]

# Run PyInstaller
PyInstaller.__main__.run(args)

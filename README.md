# ConRed (Confidentiality Redactor)

A GUI tool for batch processing documents (Word, XML, and Markdown) to replace sensitive information consistently across files.

## Features

- Process Word documents (DOCX) in two modes:
  - Full redaction mode: Process DOCX/XML pairs with replacement rules
  - Markdown conversion mode: Convert single DOCX files to Markdown
- Batch processing support for multiple documents
- Case-insensitive search and replace
- Consistency checking between document pairs
- Detailed logging of all replacements
- Modern GUI interface with:
  - Document pair management
  - Rule management (load/save replacement rules)
  - Real-time processing status
  - Detailed output display
- Standalone executable support

## Installation

1. Clone the repository:
```bash
git clone https://github.com/BetaMac/ConRed.git
cd ConRed
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running from Source

Run the GUI application:
```bash
python src/conred_gui.py
```

### Building and Running Executable

Build the standalone executable:
```bash
python src/build.py
```

The executable will be created in the `dist` directory.

### Using the Application

1. **Adding Documents**:
   - Click "Add Document Pair" to select Word documents
   - For full redaction, ensure matching XML files exist
   - For Markdown conversion only, any Word document can be used

2. **Managing Rules** (for redaction):
   - Load existing rules using "Load Rules"
   - Add new rules using the input fields
   - Save current rules using "Save Rules"

3. **Processing**:
   - Click "Process Documents" to start
   - Progress and results will be shown in the output window
   - Processed files are saved in the `data/output` directory

## Project Structure

```
ConRed/
├── src/
│   ├── conred.py           # Core processing functionality
│   ├── conred_gui.py       # GUI interface
│   ├── markdown_converter.py# Markdown conversion support
│   └── build.py            # Executable builder
├── data/
│   ├── input/              # Place input files here
│   └── output/             # Processed files appear here
├── rules/                  # Replacement rule configurations
├── logs/                   # Processing logs
└── requirements.txt        # Python dependencies
```

## Dependencies

- Python 3.6+
- customtkinter (GUI framework)
- python-docx (Word document processing)
- mammoth (Markdown conversion)
- PyInstaller (executable building)

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

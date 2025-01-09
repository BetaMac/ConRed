# ConRed (Confidentiality Redactor)

A GUI tool for batch processing document pairs (Word and XML) to replace sensitive information consistently across files.

## Features

- Process multiple DOCX/XML document pairs simultaneously
- Case-insensitive search and replace
- Consistency checking between document pairs
- Detailed logging of all replacements
- GUI interface for easy operation

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
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

Run the GUI application:
```bash
python src/conred_gui.py
```

Or build the standalone executable:
```bash
python src/build.py
```

## Project Structure

```
ConRed/
├── src/
│   ├── conred.py          # Core functionality
│   ├── conred_gui.py      # GUI interface
│   └── build.py           # Executable builder
├── data/
│   ├── input/            
│   └── output/           
├── logs/                  
└── requirements.txt       
```

## License

[Add your chosen license]

## Contributing

[Add contribution guidelines if needed]

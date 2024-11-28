import docx
import xml.etree.ElementTree as ET
import re
from collections import Counter
from pathlib import Path
import json
import logging
from datetime import datetime

class ConRed:
    def __init__(self, config_path=None):
        """
        Initialize ConRed with optional config file
        """
        self.replacement_dict = {}
        self.replacement_counts = {'word': {}, 'xml': {}}
        
        # Setup logging
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=log_dir / f'conred_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path):
        """Load replacement dictionary from JSON config file"""
        try:
            with open(config_path, 'r') as f:
                self.replacement_dict = json.load(f)
            logging.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logging.error(f"Error loading config: {str(e)}")
            raise

    def replace_text(self, text):
        """
        Perform case-insensitive replacement while preserving replacement text case
        Returns tuple of (modified text, counter of replacements)
        """
        counts = Counter()
        modified_text = text
        
        for original, replacement in self.replacement_dict.items():
            # Create case-insensitive pattern with word boundaries
            pattern = re.compile(r'\b' + re.escape(original) + r'\b', re.IGNORECASE)
            
            # Count matches before replacement
            matches = pattern.findall(modified_text)
            counts[original] = len(matches)
            
            # Perform replacement
            modified_text = pattern.sub(replacement, modified_text)
            
        return modified_text, counts

    def process_word_document(self, input_path):
        """Process a Word document and count replacements."""
        try:
            doc = docx.Document(input_path)
            modified_doc = docx.Document()
            
            self.replacement_counts['word'] = Counter()
            
            # Process each paragraph
            for paragraph in doc.paragraphs:
                new_text, counts = self.replace_text(paragraph.text)
                self.replacement_counts['word'].update(counts)
                modified_doc.add_paragraph(new_text)
            
            logging.info(f"Processed Word document: {input_path}")
            return modified_doc
            
        except Exception as e:
            logging.error(f"Error processing Word document: {str(e)}")
            raise

    def process_xml_document(self, input_path):
        """Process an XML document and count replacements."""
        try:
            tree = ET.parse(input_path)
            root = tree.getroot()
            
            self.replacement_counts['xml'] = Counter()
            
            def process_element(element):
                if element.text:
                    new_text, counts = self.replace_text(element.text)
                    self.replacement_counts['xml'].update(counts)
                    element.text = new_text
                
                for child in element:
                    process_element(child)
            
            process_element(root)
            logging.info(f"Processed XML document: {input_path}")
            return tree
            
        except Exception as e:
            logging.error(f"Error processing XML document: {str(e)}")
            raise

    def verify_counts(self):
        """Verify that replacement counts match between documents."""
        mismatches = []
        
        for word in self.replacement_dict.keys():
            word_count = self.replacement_counts['word'].get(word, 0)
            xml_count = self.replacement_counts['xml'].get(word, 0)
            
            if word_count != xml_count:
                mismatches.append({
                    'word': word,
                    'word_doc_count': word_count,
                    'xml_doc_count': xml_count
                })
        
        return mismatches

    def process_documents(self, word_input, xml_input, word_output, xml_output):
        """Process both documents and save results."""
        # Convert paths to Path objects
        word_input = Path(word_input)
        xml_input = Path(xml_input)
        word_output = Path(word_output)
        xml_output = Path(xml_output)
        
        # Ensure output directories exist
        word_output.parent.mkdir(parents=True, exist_ok=True)
        xml_output.parent.mkdir(parents=True, exist_ok=True)
        
        # Process documents
        modified_doc = self.process_word_document(word_input)
        modified_xml = self.process_xml_document(xml_input)
        
        # Save modified documents
        modified_doc.save(word_output)
        modified_xml.write(xml_output)
        
        # Verify counts and return results
        mismatches = self.verify_counts()
        
        results = {
            'mismatches': mismatches,
            'word_counts': dict(self.replacement_counts['word']),
            'xml_counts': dict(self.replacement_counts['xml'])
        }
        
        # Log results
        logging.info(f"Processing complete. Mismatches found: {len(mismatches)}")
        
        return results

def main():
    # Example configuration file (config.json)
    config = {
        'SkyPhone': 'Brand1',
        'Quantum Mobile': 'Brand2',
        'NexusWave': 'Brand3',
        'TechPro': 'Brand4',
        'SmartLife': 'Brand5',
        'TechVision Analytics': 'Client1',
        'MarketScope Research': 'Agency1'
    }
    
    # Save example config
    config_path = Path('config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    # Initialize ConRed
    conred = ConRed(config_path)
    
    # Process documents
    results = conred.process_documents(
        'data/input/questionnaire.docx',
        'data/input/questionnaire.xml',
        'data/output/questionnaire_redacted.docx',
        'data/output/questionnaire_redacted.xml'
    )
    
    # Print results
    if results['mismatches']:
        print("\nWarning: Replacement count mismatches found:")
        for mismatch in results['mismatches']:
            print(f"Word '{mismatch['word']}': "
                  f"Word doc: {mismatch['word_doc_count']}, "
                  f"XML doc: {mismatch['xml_doc_count']}")
    else:
        print("\nAll replacement counts match between documents!")
    
    print("\nReplacement counts:")
    for word, count in results['word_counts'].items():
        print(f"{word}: {count} replacements")

if __name__ == "__main__":
    main()

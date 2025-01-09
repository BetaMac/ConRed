import re
from collections import Counter
from typing import Dict, Tuple
import mammoth
import logging

class MarkdownConverter:
    """
    Handles conversion of Word documents to Markdown and subsequent text replacement.
    
    This class manages the conversion process and maintains replacement counts
    for consistency checking with other document types.
    """
    
    def __init__(self):
        """Initialize the markdown converter with a counter for replacements"""
        self.replacement_counts = Counter()
        self.replacement_dict = {}

    def set_replacement_dict(self, replacement_dict: Dict[str, str]):
        """Set the replacement dictionary for text processing"""
        self.replacement_dict = replacement_dict

    def replace_text(self, text: str) -> Tuple[str, Counter]:
        """Perform replacements using the same logic as ConRed"""
        counts = Counter()
        modified_text = text
        
        for original, replacement in self.replacement_dict.items():
            patterns = [
                r'\b' + re.escape(original) + r'\b',
                r'\b' + re.escape(original).replace('.', r'\.').replace('-', r'\-') + r'\b',
                r'(?<=__)\s*' + re.escape(original) + r'\s*(?=__)',
                r'(?<=\*\*)\s*' + re.escape(original) + r'\s*(?=\*\*)',
                r'(?<=- )' + re.escape(original),
                r'(?<=\* )' + re.escape(original),
                r'(?<=\[)' + re.escape(original) + r'(?=\])',
                r'\b' + re.escape(original).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;') + r'\b'
            ]
            
            for pattern in patterns:
                regex = re.compile(pattern, re.IGNORECASE)
                matches = regex.findall(modified_text)
                counts[original] += len(matches)
                modified_text = regex.sub(replacement, modified_text)
        
        return modified_text, counts

    def clean_markdown(self, content: str) -> str:
        """Clean markdown content by removing unnecessary elements."""
        
        # Remove base64 encoded images
        content = re.sub(r'!\[.*?\]\(data:image\/[^;]+;base64,[^)]+\)', '', content)
        
        # Remove multiple consecutive blank lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Remove any remaining base64 data
        content = re.sub(r'data:image\/[^;]+;base64,[^\s]+', '', content)
        
        # Remove any non-breaking space characters
        content = content.replace('\xa0', ' ')
        
        # Remove any remaining image references
        content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
        
        # Clean up any remaining formatting artifacts
        content = re.sub(r'\*\*\s*\*\*', '', content)  # Empty bold
        content = re.sub(r'__\s*__', '', content)      # Empty underline
        
        # Remove any trailing whitespace
        content = '\n'.join(line.rstrip() for line in content.splitlines())
        
        return content.strip()

    def process_markdown(self, markdown_content: str, replacement_dict: Dict[str, str]) -> Tuple[str, Counter]:
        """
        Process markdown content with the given replacement dictionary.
        
        Args:
            markdown_content (str): The markdown text to process
            replacement_dict (Dict[str, str]): Dictionary of terms to replace
            
        Returns:
            Tuple[str, Counter]: (Modified markdown content, Count of replacements made)
        """
        try:
            self.set_replacement_dict(replacement_dict)
            cleaned_content = self.clean_markdown(markdown_content)
            modified_markdown, counts = self.replace_text(cleaned_content)
            self.replacement_counts.update(counts)
            return modified_markdown, self.replacement_counts
            
        except Exception as e:
            logging.error(f"Error processing markdown: {str(e)}")
            raise 

    def convert_docx_to_markdown(self, docx_path: str) -> str:
        """Convert a Word document to Markdown format."""
        try:
            with open(docx_path, "rb") as docx_file:
                result = mammoth.convert_to_markdown(docx_file)
                return result.value
        except Exception as e:
            logging.error(f"Error converting DOCX to Markdown: {str(e)}")
            raise 
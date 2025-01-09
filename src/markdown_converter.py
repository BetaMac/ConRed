import mammoth
from pathlib import Path
import logging
from typing import Dict, Tuple
from collections import Counter
import re

class MarkdownConverter:
    """
    Handles conversion of Word documents to Markdown and subsequent text replacement.
    
    This class manages the conversion process and maintains replacement counts
    for consistency checking with other document types.
    """
    
    def __init__(self):
        """Initialize the markdown converter with a counter for replacements"""
        self.replacement_counts = Counter()

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

    def convert_docx_to_markdown(self, input_path: Path) -> str:
        """
        Convert Word document to Markdown while preserving basic formatting.
        
        Args:
            input_path (Path): Path to the input Word document
            
        Returns:
            str: Converted markdown content
            
        Raises:
            Exception: If conversion fails
        """
        try:
            with open(input_path, 'rb') as docx_file:
                # Use mammoth for conversion
                result = mammoth.convert_to_markdown(docx_file)
                markdown = result.value
                messages = result.messages

                # Log any conversion warnings or info messages
                for message in messages:
                    logging.info(f"Markdown conversion message: {message}")

                # Clean the markdown content before returning
                cleaned_markdown = self.clean_markdown(markdown)
                return cleaned_markdown

        except Exception as e:
            logging.error(f"Error converting to markdown: {str(e)}")
            raise

    def process_markdown(self, markdown_content: str, replacement_dict: Dict[str, str]) -> Tuple[str, Counter]:
        """
        Process markdown content with the given replacement dictionary.
        
        Note: Uses ConRed's text replacement functionality to maintain consistency
        across document types. Imported here to avoid circular imports.
        
        Args:
            markdown_content (str): The markdown text to process
            replacement_dict (Dict[str, str]): Dictionary of terms to replace
            
        Returns:
            Tuple[str, Counter]: (Modified markdown content, Count of replacements made)
        """
        # Import here to avoid circular dependency with ConRed class
        from conred import ConRed
        
        # Clean the markdown content first
        cleaned_content = self.clean_markdown(markdown_content)
        
        # Create temporary ConRed instance for consistent text replacement
        conred = ConRed()
        conred.replacement_dict = replacement_dict
        
        # Process the cleaned markdown content
        modified_markdown, counts = conred.replace_text(cleaned_content)
        
        # Update our internal counter with the new counts
        self.replacement_counts.update(counts)
        
        return modified_markdown, self.replacement_counts 
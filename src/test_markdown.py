from pathlib import Path
from markdown_converter import MarkdownConverter
from conred import ConRed

def test_markdown_conversion():
    # Create test directory if it doesn't exist
    test_dir = Path('data/test')
    test_dir.mkdir(parents=True, exist_ok=True)

    # Sample test content
    test_doc = """
    # Test Document
    
    This is a test document with some **sensitive** information.
    
    - Company: TechVision Analytics
    - Client: MarketScope Research
    - Product: SkyPhone
    
    ## Additional Information
    Some more text about Quantum Mobile and TechPro solutions.
    """

    # Write test content to file
    test_file = test_dir / 'test.md'
    with open(test_file, 'w') as f:
        f.write(test_doc)

    # Create test replacement rules
    replacement_rules = {
        'TechVision Analytics': 'Client1',
        'MarketScope Research': 'Agency1',
        'SkyPhone': 'Brand1',
        'Quantum Mobile': 'Brand2',
        'TechPro': 'Brand4'
    }

    # Process the markdown
    converter = MarkdownConverter()
    with open(test_file, 'r') as f:
        content = f.read()
    
    modified_content, counts = converter.process_markdown(content, replacement_rules)

    # Save the result
    output_file = test_dir / 'test_redacted.md'
    with open(output_file, 'w') as f:
        f.write(modified_content)

    print("Original content:")
    print("-" * 40)
    print(test_doc)
    print("\nRedacted content:")
    print("-" * 40)
    print(modified_content)
    print("\nReplacement counts:")
    print("-" * 40)
    for term, count in counts.items():
        print(f"{term}: {count} replacements")

if __name__ == "__main__":
    test_markdown_conversion() 
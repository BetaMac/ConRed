import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pathlib import Path
import json
import threading
from typing import List, Tuple, Dict
import re
import sys
import os

# Add the current directory to sys.path
if getattr(sys, 'frozen', False):
    # If the application is run as a bundle
    application_path = sys._MEIPASS
else:
    # If the application is run from a Python interpreter
    application_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, application_path)
from conred import ConRed
import logging

class ConRedGUI(ctk.CTk):
    """
    Main GUI application for ConRed document processing.
    
    Provides interface for:
    - Loading document pairs
    - Processing documents with progress tracking
    - Displaying results and mismatches
    - Handling multiple document pairs in batch
    """
    
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("ConRed - Confidentiality Redactor")
        self.geometry("800x800")
        
        # Center window at the top of the screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 800
        window_height = 800
        x_position = (screen_width - window_width) // 2
        y_position = 0  # Position at top of screen
        
        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Data storage
        self.document_pairs: List[Tuple[Path, Path]] = []
        self.replacements: Dict[str, str] = {}
        self.current_pair = 0
        self.total_pairs = 0
        
        # Create rules directory if it doesn't exist
        self.rules_dir = Path('rules')
        self.rules_dir.mkdir(exist_ok=True)
        
        # Load default config
        self.default_config = {
            'Dynata': 'Panel1',
            'Toluna': 'Panel2',
            'Global Market Insite': 'Panel3',
            'M3': 'Panel4',
            'SurveyBods': 'Panel5',
            'St Modwen Homes': 'Client1',
            'MarketScope Research': 'Agency1',
            'TechVision Analytics': 'Agency2'
        }
        
        # Try to load existing config or create default
        config_path = self.rules_dir / 'default_config.json'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    self.replacements = json.load(f)
            except Exception as e:
                self.replacements = self.default_config
                logging.error(f"Error loading default config: {str(e)}")
        else:
            # Save default config
            with open(config_path, 'w') as f:
                json.dump(self.default_config, f, indent=4)
            self.replacements = self.default_config
        
        self.create_gui()
        self.update_rules_list()  # Show the loaded rules

    def update_status(self, message, progress=None):
        """Update status bar with message and optional progress"""
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress)
        self.update_idletasks()

    def add_document_pair(self):
        """Add multiple document pairs to process"""
        word_files = filedialog.askopenfilenames(
            title="Select Word Documents",
            filetypes=[
                ("Word Documents", "*.docx;*.doc"),
                ("All Files", "*.*")
            ]
        )
        
        if not word_files:
            return
            
        for word_file in word_files:
            word_path = Path(word_file)
            xml_path = word_path.with_suffix('.xml')
            
            # Only check for XML if we have replacement rules
            if self.replacements and not xml_path.exists():
                messagebox.showwarning(
                    "Warning", 
                    f"No XML file found for {word_path.name}. Will only convert to Markdown."
                )
            
            self.document_pairs.append((word_path, xml_path if xml_path.exists() else None))
        
        self.update_document_list()
        self.update_status(f"Added {len(word_files)} document(s)")

    def clear_documents(self):
        """Clear all document pairs"""
        self.document_pairs.clear()
        self.doc_list.delete("1.0", tk.END)
        self.update_status("All documents cleared")
        self.progress_bar.set(0)

    def update_document_list(self):
        """Update the document list display"""
        self.doc_list.delete("1.0", tk.END)
        for word_path, xml_path in self.document_pairs:
            self.doc_list.insert(tk.END, f"DOCX: {word_path}\n")
            if xml_path:
                self.doc_list.insert(tk.END, f"XML: {xml_path}\n")
            else:
                self.doc_list.insert(tk.END, "XML: None (Markdown conversion only)\n")
            self.doc_list.insert(tk.END, "\n")

    def load_rules(self):
        """Load replacement rules from a JSON file"""
        file_path = filedialog.askopenfilename(
            initialdir=self.rules_dir,
            title="Select Rules File",
            filetypes=[("JSON files", "*.json")]
        )
        if not file_path:
            return
            
        try:
            with open(file_path, 'r') as f:
                loaded_rules = json.load(f)
            
            # Merge with existing rules
            self.replacements.update(loaded_rules)
            self.update_rules_list()
            self.update_status(f"Loaded rules from {Path(file_path).name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load rules: {str(e)}")

    def save_rules(self):
        """Save current replacement rules to a JSON file"""
        if not self.replacements:
            messagebox.showwarning("Warning", "No rules to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            initialdir=self.rules_dir,
            title="Save Rules As",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if not file_path:
            return
            
        try:
            with open(file_path, 'w') as f:
                json.dump(self.replacements, f, indent=4)
            self.update_status(f"Saved rules to {Path(file_path).name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save rules: {str(e)}")

    def update_rules_list(self):
        """Update the rules display"""
        self.rules_list.delete("1.0", tk.END)
        for search, replace in self.replacements.items():
            self.rules_list.insert(tk.END, f"'{search}' → '{replace}'\n")

    def add_replacement_rule(self):
        """Add a new replacement rule"""
        search = self.search_entry.get().strip()
        replace = self.replace_entry.get().strip()
        
        if not search or not replace:
            messagebox.showwarning(
                "Invalid Rule", 
                "Both search and replace terms are required"
            )
            return
            
        self.replacements[search] = replace
        self.update_rules_list()
        self.update_status(f"Added rule: '{search}' → '{replace}'")
        
        self.search_entry.delete(0, tk.END)
        self.replace_entry.delete(0, tk.END)

    def process_files(self):
        """Process all documents"""
        if not self.document_pairs:
            messagebox.showwarning("Warning", "No documents to process")
            return
            
        # Only check for replacement rules if we have XML files to process
        has_xml = any(xml_path for _, xml_path in self.document_pairs)
        if has_xml and not self.replacements:
            messagebox.showwarning("Warning", "No replacement rules defined for redaction")
            return
            
        # Clear previous output
        self.output_text.delete("1.0", tk.END)
        
        # Create ConRed instance with current rules
        processor = ConRed()
        processor.replacement_dict = self.replacements
        
        total_pairs = len(self.document_pairs)
        processed = 0
        
        for word_path, xml_path in self.document_pairs:
            try:
                self.update_status(f"Processing {word_path.name}", progress=processed/total_pairs)
                
                # Create output paths
                output_word = Path('data/output') / word_path.name
                output_xml = Path('data/output') / xml_path.name if xml_path else None
                
                if xml_path:
                    # Process both documents together
                    results = processor.process_documents(
                        word_path,
                        xml_path,
                        output_word,
                        output_xml
                    )
                    
                    # Show replacement counts in output
                    self.output_text.insert(tk.END, f"\nProcessed {word_path.name}:\n")
                    for term, count in results['word_counts'].items():
                        self.output_text.insert(tk.END, f"- '{term}' replaced {count} times in Word doc\n")
                    for term, count in results['xml_counts'].items():
                        self.output_text.insert(tk.END, f"- '{term}' replaced {count} times in XML\n")
                    for term, count in results['markdown_counts'].items():
                        self.output_text.insert(tk.END, f"- '{term}' replaced {count} times in Markdown\n")
                else:
                    # Markdown conversion only
                    try:
                        markdown_content = processor.markdown_converter.convert_docx_to_markdown(str(word_path))
                        markdown_output = Path('data/output') / word_path.with_suffix('.md').name
                        
                        # Save markdown output
                        with open(markdown_output, 'w', encoding='utf-8') as f:
                            f.write(markdown_content)
                        
                        self.output_text.insert(tk.END, f"\nConverted {word_path.name} to Markdown\n")
                        self.output_text.insert(tk.END, f"Output saved to: {markdown_output}\n")
                        
                    except Exception as e:
                        self.output_text.insert(tk.END, f"Error during markdown conversion: {str(e)}\n")
                        logging.error(f"Error during markdown conversion: {str(e)}")
                
                processed += 1
                self.update_status(
                    f"Processed {processed}/{total_pairs} documents", 
                    progress=processed/total_pairs
                )
                
            except Exception as e:
                messagebox.showerror(
                    "Error", 
                    f"Error processing {word_path.name}: {str(e)}"
                )
                logging.error(f"Error processing {word_path}: {str(e)}")
                return
                
        self.update_status("Processing complete!", progress=1.0)
        messagebox.showinfo("Success", "All documents processed successfully!")

    def create_gui(self):
        # Create main containers
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Document selection section
        doc_frame = ctk.CTkFrame(self)
        doc_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(doc_frame, text="Document Pairs").pack(pady=5)
        
        btn_frame = ctk.CTkFrame(doc_frame)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="Add Document Pair", 
            command=self.add_document_pair
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="Clear All", 
            command=self.clear_documents
        ).pack(side="left", padx=5)

        # Document list
        self.doc_list = ctk.CTkTextbox(doc_frame, height=150)
        self.doc_list.pack(fill="x", padx=5, pady=5)

        # Replacement rules section
        replace_frame = ctk.CTkFrame(self)
        replace_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        rules_header = ctk.CTkFrame(replace_frame)
        rules_header.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(rules_header, text="Replacement Rules").pack(side="left", pady=5)
        
        # Add rules file controls
        rules_file_frame = ctk.CTkFrame(rules_header)
        rules_file_frame.pack(side="right", padx=5)
        
        ctk.CTkButton(
            rules_file_frame,
            text="Load Rules",
            command=self.load_rules,
            width=100
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            rules_file_frame,
            text="Save Rules",
            command=self.save_rules,
            width=100
        ).pack(side="left", padx=2)
        
        # Rule input section
        rule_frame = ctk.CTkFrame(replace_frame)
        rule_frame.pack(fill="x", padx=5, pady=5)
        
        self.search_entry = ctk.CTkEntry(rule_frame, placeholder_text="Search for...")
        self.search_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        self.replace_entry = ctk.CTkEntry(rule_frame, placeholder_text="Replace with...")
        self.replace_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        ctk.CTkButton(
            rule_frame, 
            text="Add Rule",
            command=self.add_replacement_rule,
            width=100
        ).pack(side="left", padx=5)

        # Rules list
        self.rules_list = ctk.CTkTextbox(replace_frame, height=150)
        self.rules_list.pack(fill="x", padx=5, pady=5)

        # Output section
        output_frame = ctk.CTkFrame(self)
        output_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        output_frame.grid_rowconfigure(1, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(output_frame, text="Processing Output").grid(row=0, column=0, pady=5)
        
        self.output_text = ctk.CTkTextbox(output_frame, height=150)
        self.output_text.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Status bar
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        self.progress_bar = ctk.CTkProgressBar(status_frame)
        self.progress_bar.pack(fill="x", padx=5, pady=2)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(status_frame, text="Ready")
        self.status_label.pack(pady=2)

        # Process button
        self.process_btn = ctk.CTkButton(
            self, 
            text="Process Documents", 
            command=self.process_files
        )
        self.process_btn.grid(row=4, column=0, padx=10, pady=10)

def main():
    app = ConRedGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
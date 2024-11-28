import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pathlib import Path
import json
import threading
from typing import List, Tuple, Dict
import re
from conred import ConRed

class ConRedGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("ConRed - Confidentiality Redactor")
        self.geometry("800x600")
        
        # Data storage
        self.document_pairs: List[Tuple[Path, Path]] = []
        self.replacements: Dict[str, str] = {}
        self.current_pair = 0
        self.total_pairs = 0
        
        self.create_gui()

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
        self.doc_list = ctk.CTkTextbox(doc_frame, height=100)
        self.doc_list.pack(fill="x", padx=5, pady=5)

        # Replacement rules section
        replace_frame = ctk.CTkFrame(self)
        replace_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(replace_frame, text="Replacement Rules").pack(pady=5)
        
        rule_frame = ctk.CTkFrame(replace_frame)
        rule_frame.pack(fill="x", padx=5, pady=5)
        
        self.search_entry = ctk.CTkEntry(rule_frame, placeholder_text="Search for...")
        self.search_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        self.replace_entry = ctk.CTkEntry(rule_frame, placeholder_text="Replace with...")
        self.replace_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        ctk.CTkButton(
            rule_frame, 
            text="Add Rule", 
            command=self.add_replacement_rule
        ).pack(side="left", padx=5)

        # Rules list
        self.rules_list = ctk.CTkTextbox(replace_frame, height=100)
        self.rules_list.pack(fill="x", padx=5, pady=5)

        # Output section
        output_frame = ctk.CTkFrame(self)
        output_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        
        ctk.CTkLabel(output_frame, text="Processing Output").pack(pady=5)
        
        self.output_text = ctk.CTkTextbox(output_frame)
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)

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
            command=self.process_documents
        )
        self.process_btn.grid(row=4, column=0, padx=10, pady=10)

    def update_status(self, message, progress=None):
        """Update status bar with message and optional progress"""
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress)
        self.update_idletasks()

    def add_document_pair(self):
        word_file = filedialog.askopenfilename(
            filetypes=[("Word Documents", "*.docx;*.doc")]
        )
        if not word_file:
            return
            
        word_path = Path(word_file)
        xml_path = word_path.with_suffix('.xml')
        
        if not xml_path.exists():
            messagebox.showerror(
                "Error", 
                f"Corresponding XML file not found: {xml_path}"
            )
            return
            
        self.document_pairs.append((word_path, xml_path))
        self.update_document_list()
        self.update_status(f"Added document pair: {word_path.name}")

    def clear_documents(self):
        self.document_pairs.clear()
        self.doc_list.delete("1.0", tk.END)
        self.update_status("All documents cleared")
        self.progress_bar.set(0)

    def add_replacement_rule(self):
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
        self.update_status(f"Added replacement rule: '{search}' → '{replace}'")
        
        self.search_entry.delete(0, tk.END)
        self.replace_entry.delete(0, tk.END)

    def update_document_list(self):
        self.doc_list.delete("1.0", tk.END)
        for word_path, xml_path in self.document_pairs:
            self.doc_list.insert(tk.END, f"DOCX: {word_path}\nXML: {xml_path}\n\n")

    def update_rules_list(self):
        self.rules_list.delete("1.0", tk.END)
        for search, replace in self.replacements.items():
            self.rules_list.insert(tk.END, f"'{search}' → '{replace}'\n")

    def process_documents(self):
        if not self.document_pairs:
            messagebox.showerror("Error", "No document pairs added")
            return
            
        if not self.replacements:
            messagebox.showerror("Error", "No replacement rules defined")
            return
            
        self.process_btn.configure(state="disabled")
        self.output_text.delete("1.0", tk.END)
        self.current_pair = 0
        self.total_pairs = len(self.document_pairs)
        
        # Save replacement rules to temporary config
        config_path = Path('temp_config.json')
        with open(config_path, 'w') as f:
            json.dump(self.replacements, f, indent=4)
        
        def process():
            conred = ConRed(config_path)
            
            for i, (word_path, xml_path) in enumerate(self.document_pairs, 1):
                self.current_pair = i
                progress = i / self.total_pairs
                self.update_status(
                    f"Processing pair {i} of {self.total_pairs}: {word_path.name}",
                    progress
                )
                
                self.output_text.insert(tk.END, f"\nProcessing pair:\n{word_path}\n{xml_path}\n")
                self.output_text.insert(tk.END, "-" * 50 + "\n")
                
                # Create output paths
                word_output = word_path.parent / 'output' / f'{word_path.stem}_redacted{word_path.suffix}'
                xml_output = xml_path.parent / 'output' / f'{xml_path.stem}_redacted{xml_path.suffix}'
                
                try:
                    results = conred.process_documents(
                        word_path, xml_path, word_output, xml_output
                    )
                    
                    if results['mismatches']:
                        self.output_text.insert(tk.END, "\nWarning: Replacement count mismatches found:\n")
                        for mismatch in results['mismatches']:
                            self.output_text.insert(
                                tk.END,
                                f"Word '{mismatch['word']}': "
                                f"Word doc: {mismatch['word_doc_count']}, "
                                f"XML doc: {mismatch['xml_doc_count']}\n"
                            )
                    else:
                        self.output_text.insert(tk.END, "\nAll replacement counts match!\n")
                    
                    self.output_text.insert(tk.END, "\nReplacement counts:\n")
                    for word, count in results['word_counts'].items():
                        self.output_text.insert(tk.END, f"{word}: {count} replacements\n")
                    
                except Exception as e:
                    self.output_text.insert(tk.END, f"\nError processing documents: {str(e)}\n")
                    self.update_status(f"Error processing {word_path.name}", progress)
                
                self.output_text.insert(tk.END, "\n" + "="*50 + "\n")
                self.output_text.see(tk.END)
            
            config_path.unlink()  # Remove temporary config file
            self.process_btn.configure(state="normal")
            self.update_status("Processing complete!", 1.0)
        
        # Run processing in a separate thread
        threading.Thread(target=process, daemon=True).start()

def main():
    app = ConRedGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
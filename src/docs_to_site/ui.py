import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pathlib import Path
from .converter import DocumentConverter

class ConverterUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Docs-to-Site Converter")
        self.window.geometry("600x400")
        
        # Input/Output paths
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Input folder section
        input_frame = ttk.LabelFrame(self.window, text="Input Folder", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Entry(input_frame, textvariable=self.input_path, width=50).pack(side="left", padx=5)
        ttk.Button(input_frame, text="Browse", command=self._browse_input).pack(side="left")
        
        # Output folder section
        output_frame = ttk.LabelFrame(self.window, text="Output Folder", padding="10")
        output_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Entry(output_frame, textvariable=self.output_path, width=50).pack(side="left", padx=5)
        ttk.Button(output_frame, text="Browse", command=self._browse_output).pack(side="left")
        
        # Status section
        self.status_frame = ttk.LabelFrame(self.window, text="Status", padding="10")
        self.status_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.status_text = tk.Text(self.status_frame, height=10, width=50)
        self.status_text.pack(fill="both", expand=True)
        
        # Convert button
        self.convert_btn = ttk.Button(
            self.window, 
            text="Convert Documents", 
            command=self._convert_documents
        )
        self.convert_btn.pack()
        
    def _browse_input(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_path.set(folder)
            
    def _browse_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_path.set(folder)
            
    def _convert_documents(self):
        input_path = self.input_path.get()
        output_path = self.output_path.get()
        
        if not input_path or not output_path:
            messagebox.showerror("Error", "Please select both input and output folders")
            return
            
        try:
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, "Converting documents...\n")
            self.window.update()
            
            converter = DocumentConverter(Path(input_path), Path(output_path))
            converter.convert()
            
            self.status_text.insert(tk.END, "Conversion completed successfully!\n")
            messagebox.showinfo("Success", "Documents converted successfully!")
            
        except Exception as e:
            self.status_text.insert(tk.END, f"Error: {str(e)}\n")
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")
            
    def run(self):
        self.window.mainloop() 
"""
Graphical user interface for the document converter.
"""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
from pathlib import Path
import logging
import threading
from typing import Optional

from .converter import Converter

logger = logging.getLogger(__name__)


class ConverterUI:
    """Graphical user interface for the document converter."""
    
    def __init__(self):
        """Initialize the UI."""
        self.window = tk.Tk()
        self.window.title("Docs-to-Site Converter")
        self.window.geometry("800x600")
        
        # Input/Output paths
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        
        # Conversion state
        self.is_converting = False
        self.converter: Optional[Converter] = None
        
        self._create_widgets()
        self._setup_logging()
    
    def _create_widgets(self):
        """Create and arrange all UI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Path selection section
        self._create_path_section(main_frame)
        
        # Progress section
        self._create_progress_section(main_frame)
        
        # Status section
        self._create_status_section(main_frame)
        
        # Action buttons
        self._create_action_buttons(main_frame)
    
    def _create_path_section(self, parent):
        """Create the path selection section."""
        paths_frame = ttk.LabelFrame(parent, text="Document Paths", padding="10")
        paths_frame.pack(fill="x", pady=(0, 10))
        
        # Input folder
        input_frame = ttk.Frame(paths_frame)
        input_frame.pack(fill="x", pady=(0, 5))
        ttk.Label(input_frame, text="Input:").pack(side="left", padx=(0, 5))
        ttk.Entry(input_frame, textvariable=self.input_path).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(input_frame, text="Browse", command=self._browse_input).pack(side="left")
        
        # Output folder
        output_frame = ttk.Frame(paths_frame)
        output_frame.pack(fill="x")
        ttk.Label(output_frame, text="Output:").pack(side="left", padx=(0, 5))
        ttk.Entry(output_frame, textvariable=self.output_path).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self._browse_output).pack(side="left")
    
    def _create_progress_section(self, parent):
        """Create the progress tracking section."""
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding="10")
        progress_frame.pack(fill="x", pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill="x", pady=(0, 5))
        
        # Status labels
        status_frame = ttk.Frame(progress_frame)
        status_frame.pack(fill="x")
        
        # Current file
        self.current_file_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.current_file_var).pack(side="left")
        
        # Statistics
        self.stats_var = tk.StringVar()
        ttk.Label(status_frame, textvariable=self.stats_var).pack(side="right")
    
    def _create_status_section(self, parent):
        """Create the status log section."""
        status_frame = ttk.LabelFrame(parent, text="Status Log", padding="10")
        status_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Status text with scrollbar
        self.status_text = scrolledtext.ScrolledText(
            status_frame,
            height=10,
            wrap=tk.WORD
        )
        self.status_text.pack(fill="both", expand=True)
    
    def _create_action_buttons(self, parent):
        """Create the action buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x")
        
        # Convert button
        self.convert_btn = ttk.Button(
            button_frame,
            text="Convert Documents",
            command=self._start_conversion,
            style="Accent.TButton"
        )
        self.convert_btn.pack(side="left", padx=5)
        
        # Cancel button (initially disabled)
        self.cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel_conversion,
            state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=5)
        
        # Open output button
        self.open_output_btn = ttk.Button(
            button_frame,
            text="Open Output Folder",
            command=self._open_output_folder,
            state="disabled"
        )
        self.open_output_btn.pack(side="right", padx=5)
    
    def _setup_logging(self):
        """Set up logging to the status text widget."""
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.insert(tk.END, msg + "\n")
                self.text_widget.see(tk.END)
                self.text_widget.update()
        
        # Add handler to logger
        handler = TextHandler(self.status_text)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
    
    def _browse_input(self):
        """Browse for input folder."""
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_path.set(folder)
    
    def _browse_output(self):
        """Browse for output folder."""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_path.set(folder)
    
    def _start_conversion(self):
        """Start the conversion process in a separate thread."""
        if not self.input_path.get() or not self.output_path.get():
            messagebox.showerror("Error", "Please select both input and output folders")
            return
        
        # Disable inputs during conversion
        self._set_converting_state(True)
        
        # Clear status
        self.status_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.current_file_var.set("Starting conversion...")
        self.stats_var.set("")
        
        # Start conversion thread
        thread = threading.Thread(target=self._convert_documents)
        thread.daemon = True
        thread.start()
    
    def _convert_documents(self):
        """Convert documents in a background thread."""
        try:
            # Initialize converter
            self.converter = Converter(Path(self.input_path.get()), Path(self.output_path.get()))
            
            # Get documents
            documents = self.converter.document_converter.get_documents()
            if not documents:
                raise ValueError(f"No supported documents found in {self.input_path.get()}")
            
            # Set initial state
            self.converter.total = len(documents)
            self.converter.succeeded = 0
            current = 0
            
            # Convert each document
            for doc, is_accessible in documents:
                if not self.is_converting:  # Check for cancellation
                    break
                
                current += 1
                progress = (current / self.converter.total) * 100
                self.progress_var.set(progress)
                self.current_file_var.set(f"Converting: {doc.name}")
                
                if not is_accessible:
                    logger.warning(f"Cannot access: {doc.name}")
                    self.converter.inaccessible_files.append(doc)
                    continue
                
                try:
                    self.converter.document_converter.convert_document(doc)
                    self.converter.succeeded += 1
                    logger.info(f"Successfully converted: {doc.name}")
                except (PermissionError, OSError):
                    logger.warning(f"Cannot access: {doc.name}")
                    self.converter.inaccessible_files.append(doc)
                except Exception as e:
                    logger.error(f"Failed to convert {doc.name}: {str(e)}")
                    self.converter.conversion_errors.append((doc, str(e)))
                
                self._update_stats()
            
            if self.is_converting:  # Only if not cancelled
                # Generate MkDocs configuration
                self.current_file_var.set("Generating MkDocs configuration...")
                self.converter.mkdocs.generate(self.converter.document_converter.converted_files)
                
                # Show completion message
                self._show_completion_message()
        
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")
        
        finally:
            if self.converter:
                self.converter.cleanup()
            self._set_converting_state(False)
            self.current_file_var.set("Ready")
            self._update_stats()  # Final stats update
    
    def _update_stats(self):
        """Update the statistics display."""
        if not self.converter:
            return
            
        success_rate = (self.converter.succeeded / self.converter.total * 100) if self.converter.total > 0 else 0
        stats = (
            f"Progress: {self.converter.succeeded}/{self.converter.total} "
            f"({success_rate:.1f}%)"
        )
        
        if self.converter.failed_count:
            stats += f" | Failed: {self.converter.failed_count}"
        if self.converter.inaccessible_count:
            stats += f" | Inaccessible: {self.converter.inaccessible_count}"
        
        self.stats_var.set(stats)
    
    def _show_completion_message(self):
        """Show the completion message with statistics."""
        if not self.converter or self.converter.total == 0:
            return
            
        success_rate = (self.converter.succeeded / self.converter.total) * 100
        
        if success_rate == 100:
            messagebox.showinfo(
                "Success",
                "All documents converted successfully!"
            )
        else:
            details = (
                f"Converted {self.converter.succeeded} out of {self.converter.total} documents.\n"
                f"Success rate: {success_rate:.1f}%\n"
            )
            
            if self.converter.failed_count:
                details += f"Failed: {self.converter.failed_count}\n"
            if self.converter.inaccessible_count:
                details += f"Inaccessible: {self.converter.inaccessible_count}\n"
            
            details += "\nCheck the status log for details."
            
            messagebox.showwarning("Partial Success", details)
            
        # Enable the open output folder button
        self.open_output_btn.configure(state="normal")
    
    def _cancel_conversion(self):
        """Cancel the ongoing conversion."""
        self.is_converting = False
        self.current_file_var.set("Cancelling...")
    
    def _open_output_folder(self):
        """Open the output folder in the system file explorer."""
        import os
        import subprocess
        
        output_path = self.output_path.get()
        if not output_path:
            return
        
        # Convert to absolute Path object and resolve any symlinks
        folder_path = Path(output_path).resolve()
        
        # Check if folder exists, create if it doesn't
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create output folder: {e}")
            messagebox.showerror(
                "Error",
                f"Could not create the output folder:\n{folder_path}\n\n{str(e)}"
            )
            return
        
        try:
            if os.name == 'nt':  # Windows
                # Use string representation and normalize slashes for Windows
                folder_str = str(folder_path).replace('/', '\\')
                # For Windows, use 'explorer' to open the folder
                os.startfile(folder_str)
            elif os.name == 'posix':  # macOS and Linux
                folder_str = str(folder_path)
                if os.uname().sysname == 'Darwin':  # macOS
                    subprocess.run(['open', folder_str], check=True)
                else:  # Linux
                    subprocess.run(['xdg-open', folder_str], check=True)
            
            logger.info(f"Opened output folder: {folder_path}")
        except Exception as e:
            logger.error(f"Failed to open output folder: {e}")
            messagebox.showerror(
                "Error",
                f"Could not open the output folder:\n{folder_path}\n\nError: {str(e)}"
            )
    
    def _set_converting_state(self, converting: bool):
        """Update UI state based on conversion status."""
        self.is_converting = converting
        
        # Update button states
        self.convert_btn.configure(state="disabled" if converting else "normal")
        self.cancel_btn.configure(state="normal" if converting else "disabled")
        self.open_output_btn.configure(state="disabled" if converting else "normal")
        
        # Update input states
        state = "disabled" if converting else "normal"
        for widget in self.window.winfo_children():
            if isinstance(widget, (ttk.Entry, ttk.Button)) and widget not in (self.convert_btn, self.cancel_btn):
                widget.configure(state=state)
    
    def run(self):
        """Start the UI main loop."""
        self.window.mainloop()

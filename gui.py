import tkinter as tk
from tkinter import filedialog, messagebox
from tkintertable import TableCanvas, TableModel
import os
import subprocess

import json


class ScrapyRunnerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Scrapy Runner")
        self.master.geometry("800x600")  # Default window size

        self.create_widgets()

    def create_widgets(self):
        # Fullscreen button
        self.fullscreen_button = tk.Button(self.master, text="Toggle Fullscreen", command=self.toggle_fullscreen)
        self.fullscreen_button.pack(anchor=tk.NE, padx=10, pady=10)

        # Frame for input/output
        self.frame_io = tk.Frame(self.master, padx=10, pady=10)
        self.frame_io.pack(fill=tk.BOTH, expand=False)

        # Input: Spider file selection
        tk.Label(self.frame_io, text="Spider file:").grid(row=0, column=0, sticky='w')
        self.spider_file_entry = tk.Entry(self.frame_io, width=50)
        self.spider_file_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.frame_io, text="Browse...", command=self.browse_spider_file).grid(row=0, column=2, padx=5,
                                                                                         pady=5)

        # Output: JSON file selection
        tk.Label(self.frame_io, text="Output JSON file:").grid(row=1, column=0, sticky='w')
        self.output_file_entry = tk.Entry(self.frame_io, width=50)
        self.output_file_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.frame_io, text="Browse...", command=self.browse_output_file).grid(row=1, column=2, padx=5,
                                                                                         pady=5)

        # Button to run Scrapy spider
        tk.Button(self.frame_io, text="Run Spider", command=self.run_spider).grid(row=2, column=1, padx=5, pady=10)

        # Frame for displaying data with scrollbar
        self.frame_display = tk.Frame(self.master, padx=10, pady=10)
        self.frame_display.pack(fill=tk.BOTH, expand=True)

        # TableCanvas for displaying data
        self.table = TableCanvas(self.frame_display)
        self.table.show()

    def toggle_fullscreen(self):
        # Toggle fullscreen mode
        self.master.attributes('-fullscreen', not self.master.attributes('-fullscreen'))

    def browse_spider_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if filename:
            self.spider_file_entry.delete(0, tk.END)
            self.spider_file_entry.insert(tk.END, filename)

    def browse_output_file(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            self.output_file_entry.delete(0, tk.END)
            self.output_file_entry.insert(tk.END, filename)
            self.load_json_data(filename)

    def run_spider(self):
        spider_file = self.spider_file_entry.get()
        output_file = self.output_file_entry.get()

        if not spider_file or not output_file:
            messagebox.showerror("Error", "Please select both Spider file and Output file.")
            return

        # Check if spider file exists
        if not os.path.exists(spider_file):
            messagebox.showerror("Error", "Spider file not found.")
            return

        # Run the scrapy command
        command = f"scrapy runspider {spider_file} -o {output_file}"
        try:
            subprocess.run(command, shell=True, check=True)
            messagebox.showinfo("Success", "Spider run successfully.")
            self.load_json_data(output_file)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error running spider:\n{e}")

    def load_json_data(self, filename):
        # Clear existing data
        self.table.model.importDict({})

        # Load JSON data
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Prepare data for table
            table_data = {}
            for i, entry in enumerate(data, start=1):
                table_data[i] = {
                    "Country": entry.get('Country', ''),
                    "Domain": entry.get('Domain', ''),
                    "Rental Object": entry.get('Rental Object', ''),
                    "Title": entry.get('Title', ''),
                    "Link": entry.get('Link', ''),
                    "Price": entry.get('Price', ''),
                    "Description": entry.get('Description', ''),
                    "Phone": entry.get('Phone', ''),
                    "Email": entry.get('Email', '')
                }

            # Display data in table
            self.table.model.importDict(table_data)
            self.table.redraw()

        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Error loading JSON file:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error:\n{e}")


def main():
    root = tk.Tk()
    app = ScrapyRunnerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
import tkinter as tk
from tkinter import scrolledtext
import os
import platform
import getpass
import argparse

class ShellEmulator(tk.Tk):
    def __init__(self, vfs_path=None, startup_script=None):
        super().__init__()
        
        self.vfs_path = vfs_path
        self.startup_script = startup_script
        self.history = []
        self.history_index = -1
        
        self._setup_ui()
        self._display_welcome()
        
        if startup_script:
            self.after(100, self._run_startup_script)
        else:
            self._display_prompt()

    def _setup_ui(self):
        self.title(self._get_window_title())
        self.geometry("800x600")
        
        # Output
        self.output_area = scrolledtext.ScrolledText(
            self, state='disabled', wrap='word', 
            bg='black', fg='white', font=('Consolas', 12)
        )
        self.output_area.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Input
        input_frame = tk.Frame(self, bg='black')
        input_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(input_frame, text=">", fg='white', bg='black', font=('Consolas', 12)).pack(side='left')
        
        self.input_entry = tk.Entry(
            input_frame, bg='black', fg='white', 
            insertbackground='white', font=('Consolas', 12)
        )
        self.input_entry.pack(side='left', expand=True, fill='x', padx=(0, 5))
        self.input_entry.focus_set()
        self.input_entry.bind("<Return>", self._on_enter)
        self.input_entry.bind("<Up>", self._history_up)
        self.input_entry.bind("<Down>", self._history_down)

    def _get_window_title(self):
        username = getpass.getuser()
        hostname = platform.node()
        return f"Эмулятор - [{username}@{hostname}]"

    def _display_welcome(self):
        self._display_output("Welcome to the Shell Emulator!")
        self._display_output(f"VFS path: {self.vfs_path}")
        self._display_output(f"Startup script: {self.startup_script}")

    def _display_output(self, text):
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.config(state='disabled')
        self.output_area.see(tk.END)

    def _display_prompt(self):
        self.input_entry.delete(0, tk.END)
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, "> ")
        self.output_area.config(state='disabled')
        self.output_area.see(tk.END)

    def _on_enter(self, event=None):
        command = self.input_entry.get().strip()
        if not command:
            return
        
        self.history.append(command)
        self.history_index = len(self.history)
        
        self._display_output(f"> {command}")
        self._execute_command(command)
        self._display_prompt()

    def _history_up(self, event=None):
        if self.history and self.history_index > 0:
            self.history_index -= 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.history[self.history_index])
        return "break"
    
    def _history_down(self, event=None):
        if self.history and self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.history[self.history_index])
        return "break"

    def _execute_command(self, command_line):
        parts = command_line.split()
        if not parts:
            return
        
        parts = [os.path.expandvars(part) for part in parts]
        command, args = parts[0], parts[1:]
        
        if command == "ls":
            self._display_output(f"ls: {args}")
        elif command == "cd":
            self._display_output(f"cd: {args}" if args else "cd: missing argument")
        elif command == "exit":
            self.quit()
        else:
            self._display_output(f"Command not found: {command}")

    def _run_startup_script(self):
        try:
            with open(self.startup_script, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self._display_output(f"> {line}")
                        self._execute_command(line)
        except Exception as e:
            self._display_output(f"Error executing script: {e}")
        
        self._display_prompt()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Shell Emulator')
    parser.add_argument('--vfs-path', help='Path to VFS')
    parser.add_argument('--startup-script', help='Path to startup script')
    
    args = parser.parse_args()
    app = ShellEmulator(args.vfs_path, args.startup_script)
    app.mainloop()
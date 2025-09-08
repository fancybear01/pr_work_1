import tkinter as tk
from tkinter import scrolledtext
import os
import platform
import getpass

class ShellEmulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(self._get_window_title())
        self.geometry("800x600")

        self.history = []
        self.history_index = -1

        self._create_widgets()
        self.bind("<Return>", self._on_enter)
        self.bind("<Up>", self._history_up)
        self.bind("<Down>", self._history_down)

        self._display_output("Welcome to the Shell Emulator!")
        self._display_prompt()

    def _get_window_title(self):
        username = getpass.getuser()
        hostname = platform.node()
        return f"Эмулятор - [{username}@{hostname}]"

    def _create_widgets(self):
        # Output 
        self.output_area = scrolledtext.ScrolledText(self, state='disabled', wrap='word', bg='black', fg='white', font=('Consolas', 12))
        self.output_area.pack(expand=True, fill='both', padx=5, pady=5)

        # Input 
        self.input_frame = tk.Frame(self, bg='black')
        self.input_frame.pack(fill='x', padx=5, pady=5)

        self.prompt_label = tk.Label(self.input_frame, text=">", fg='white', bg='black', font=('Consolas', 12))
        self.prompt_label.pack(side='left')

        self.input_entry = tk.Entry(self.input_frame, bg='black', fg='white', insertbackground='white', font=('Consolas', 12))
        self.input_entry.pack(side='left', expand=True, fill='x', padx=(0, 5))
        self.input_entry.focus_set()

    def _display_output(self, text):
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.config(state='disabled')
        self.output_area.see(tk.END)

    def _display_prompt(self):
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, f"\n{self.prompt_label.cget('text')} ", ('prompt',))
        self.output_area.config(state='disabled')
        self.output_area.see(tk.END)
        self.input_entry.delete(0, tk.END)

    def _on_enter(self, event=None):
        command_line = self.input_entry.get().strip()
        if not command_line:
            self._display_prompt()
            return

        self.history.append(command_line)
        self.history_index = len(self.history)

        self._display_output(f"> {command_line}")
        self._execute_command(command_line)
        self._display_prompt()

    def _history_up(self, event=None):
        if self.history:
            self.history_index = max(0, self.history_index - 1)
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.history[self.history_index])
        return "break" 
    
    def _history_down(self, event=None):
        if self.history:
            self.history_index = min(len(self.history), self.history_index + 1)
            if self.history_index == len(self.history):
                self.input_entry.delete(0, tk.END)
            else:
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, self.history[self.history_index])
        return "break" 

    def _parse_and_expand(self, command_line):
        parts = command_line.split()
        expanded_parts = []
        for part in parts:
            if '$' in part:
                expanded_part = os.path.expandvars(part)
                expanded_parts.append(expanded_part)
            else:
                expanded_parts.append(part)
        return expanded_parts

    def _execute_command(self, command_line):
        parsed_command = self._parse_and_expand(command_line)
        if not parsed_command:
            return

        command = parsed_command[0]
        args = parsed_command[1:]

        if command == "ls":
            self._command_ls(args)
        elif command == "cd":
            self._command_cd(args)
        elif command == "exit":
            self._command_exit()
        else:
            self._display_output(f"Error: Command not found: {command}")

    # команды
    def _command_ls(self, args):
        self._display_output(f"ls command executed with arguments: {args}")
        if not args:
            self._display_output(" (No arguments provided)")

    def _command_cd(self, args):
        self._display_output(f"cd command executed with arguments: {args}")
        if not args:
            self._display_output("Error: cd: missing argument")
        else:
            self._display_output(f" (Changing directory to '{args[0]}')")

    def _command_exit(self):
        self._display_output("Exiting emulator. Goodbye!")
        self.after(500, self.destroy) 

if __name__ == "__main__":
    app = ShellEmulator()
    app.mainloop()
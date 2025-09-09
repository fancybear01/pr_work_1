import tkinter as tk
from tkinter import scrolledtext
import os
import platform
import getpass
import argparse
import base64
import zipfile

class ShellEmulator(tk.Tk):
    def __init__(self, vfs_path=None, startup_script=None):
        super().__init__()
        
        self.vfs_path = vfs_path
        self.startup_script = startup_script
        
        self.vfs = {} 
        self.current_vfs_dir = "/"  
        
        self.history = []
        self.history_index = -1
        
        self._setup_ui()
        self._display_welcome()
        
        if vfs_path:
            self._load_vfs(vfs_path)
        
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
            self._command_ls(args)
        elif command == "cd":
            self._command_cd(args)
        elif command == "vfs-init":
            self._command_vfs_init(args)
        elif command == "exit":
            self.quit()
        else:
            self._display_output(f"Command not found: {command}")

    def _command_vfs_init(self, args):
        self.vfs = {}
        self.current_vfs_dir = "/"
        self._display_output("VFS initialized to empty state")
        
        if self.vfs_path and os.path.exists(self.vfs_path):
            os.remove(self.vfs_path)
            self._display_output(f"Physical VFS file removed: {self.vfs_path}")

    def _command_ls(self, args):
        if not self.vfs:
            self._display_output("No VFS loaded. Use 'vfs-init' to initialize or provide VFS path at startup.")
            return
        
        dir_contents = []
        current_dir = self.current_vfs_dir.rstrip('/') + '/'
        
        for path in self.vfs.keys():
            if path.startswith(current_dir) and path != current_dir:
                rel_path = path[len(current_dir):]
                if '/' in rel_path:
                    name = rel_path.split('/')[0]
                    if name and name not in dir_contents:
                        dir_contents.append(name)
                else:
                    dir_contents.append(rel_path)
        
        if dir_contents:
            self._display_output(" ".join(dir_contents))
        else:
            self._display_output("(empty directory)")

    def _command_cd(self, args):
        if not self.vfs:
            self._display_output("No VFS loaded. Use 'vfs-init' to initialize or provide VFS path at startup.")
            return
        
        if not args:
            self._display_output("cd: missing argument")
            return
        
        target_dir = args[0]
        
        if target_dir.startswith('/'):
            new_dir = target_dir
        else:
            current_dir = self.current_vfs_dir.rstrip('/') + '/'
            new_dir = os.path.join(current_dir, target_dir).replace('\\', '/')
        
        if not new_dir.endswith('/'):
            new_dir += '/'
        
        dir_exists = False
        for path in self.vfs.keys():
            if path == new_dir.rstrip('/') or path.startswith(new_dir):
                dir_exists = True
                break
        
        if dir_exists:
            self.current_vfs_dir = new_dir
            self._display_output(f"Changed VFS directory to {new_dir}")
        else:
            self._display_output(f"cd: {target_dir}: No such directory in VFS")

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
        
    def _load_vfs(self, zip_path):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                
                all_paths = zip_ref.namelist()
                if not all_paths:
                    self._display_output("Empty VFS archive")
                    return
                
                common_prefix = os.path.commonprefix(all_paths)
                if common_prefix and not common_prefix.endswith('/'):
                    common_prefix = common_prefix.rsplit('/', 1)[0] + '/'
                
                self._display_output(f"Common prefix: '{common_prefix}'")
                
                for file_info in zip_ref.infolist():
                    file_path = file_info.filename
                    if common_prefix and file_path.startswith(common_prefix):
                        file_path = file_path[len(common_prefix):]
                    
                    if not file_path:
                        continue
                    
                    if file_info.is_dir():
                        self.vfs[file_path] = {
                            'type': 'directory'
                        }
                    else:
                        with zip_ref.open(file_info) as file:
                            content = file.read()
                            
                        try:
                            content_str = content.decode('utf-8')
                            self.vfs[file_info.filename] = {
                                'type': 'file',
                                'content': content_str,
                                'is_binary': False
                            }
                        except UnicodeDecodeError:
                            content_b64 = base64.b64encode(content).decode('utf-8')
                            self.vfs[file_info.filename] = {
                                'type': 'file',
                                'content': content_b64,
                                'is_binary': True
                            }
            
            self._display_output(f"VFS loaded from {zip_path}")
            self._display_output(f"Files in VFS: {list(self.vfs.keys())}")
            
        except FileNotFoundError:
            self._display_output(f"Error: VFS file not found: {zip_path}")
        except zipfile.BadZipFile:
            self._display_output(f"Error: Invalid ZIP format: {zip_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Shell Emulator')
    parser.add_argument('--vfs-path', help='Path to VFS')
    parser.add_argument('--startup-script', help='Path to startup script')
    
    args = parser.parse_args()
    app = ShellEmulator(args.vfs_path, args.startup_script)
    app.mainloop()
# Last updated: 2025-05-21 23:02:46

import os
import subprocess
import sys # To get the python interpreter path
import json # Example for parsing parameters, could be simpler

# --- Configuration ---
# Get the directory of the current custom node file
NODE_DIR = os.path.dirname(os.path.abspath(__file__))
PORTABLE_SCRIPTS_SUBDIR = "portable_scripts"
PORTABLE_SCRIPTS_PATH = os.path.join(NODE_DIR, PORTABLE_SCRIPTS_SUBDIR)

# --- Helper Function to Get Script Choices ---
def get_script_choices():
    if not os.path.exists(PORTABLE_SCRIPTS_PATH):
        os.makedirs(PORTABLE_SCRIPTS_PATH, exist_ok=True) # Create if it doesn't exist
        return ["No scripts found"] # Return a default if dir was just created
        
    scripts = [f for f in os.listdir(PORTABLE_SCRIPTS_PATH) if f.endswith(".py") and os.path.isfile(os.path.join(PORTABLE_SCRIPTS_PATH, f))]
    if not scripts:
        return ["No scripts found"]
    # Optional: Add a way to get display names from within the scripts (e.g., a comment)
    # For now, just use filenames.
    return sorted(scripts)

class PortableScriptExecutor:
    CATEGORY = "自动数据"

    # Pre-populate script choices when ComfyUI loads the node
    SCRIPT_FILES = get_script_choices()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "selected_script": (s.SCRIPT_FILES, ),
                "target_folder": ("STRING", {"default": "X:/path/to/your/target_folder", "multiline": False}),
                "script_parameters": ("STRING", {"default": "# Enter parameters here, e.g., --threshold 40 --format png\n# Or JSON: {\"threshold\": 40, \"format\": \"png\"}", "multiline": True}),
                "trigger": ("*",), # Special type that accepts any connection to trigger
            },
            "optional": {
                # You could add an option to select the Python interpreter if needed
                # "python_interpreter": ("STRING", {"default": sys.executable, "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",) # Status message
    RETURN_NAMES = ("status",)
    FUNCTION = "execute_portable_script"

    def execute_portable_script(self, selected_script, target_folder, script_parameters, trigger, python_interpreter=None):
        if selected_script == "No scripts found":
            return ("No script selected or no scripts available in portable_scripts folder.",)

        script_full_path = os.path.join(PORTABLE_SCRIPTS_PATH, selected_script)

        if not os.path.isfile(script_full_path):
            return (f"ERROR: Script '{selected_script}' not found at '{script_full_path}'.",)
        
        if not os.path.isdir(target_folder):
            return (f"ERROR: Target folder '{target_folder}' does not exist or is not a directory.",)

        # Determine Python interpreter
        interpreter_to_use = python_interpreter if python_interpreter else sys.executable

        # --- Command Construction ---
        # The script will receive the target_folder as the first argument.
        # Additional parameters from the script_parameters string will be appended.
        # This example assumes parameters are space-separated, like command-line args.
        # Your scripts in `portable_scripts` will need to be able to parse these.
        
        cmd = [interpreter_to_use, script_full_path, "--target_folder", target_folder]
        
        # Simple parsing of script_parameters: split by space.
        # This is basic; for complex args (with spaces in values), your scripts
        # would need more robust parsing (like using argparse and passing quoted strings).
        # Or, you could enforce JSON for script_parameters.
        
        # Example: if script_parameters is like: --min_width 40 --min_height 40 --verbose
        # It will be split into ['--min_width', '40', '--min_height', '40', '--verbose']
        # Ensure your portable scripts use something like `argparse` to handle these.
        
        # Remove comments from parameters
        params_lines = [line.strip() for line in script_parameters.splitlines() if line.strip() and not line.strip().startswith("#")]
        processed_parameters = " ".join(params_lines).split() # Split into a list of arguments

        cmd.extend(processed_parameters)

        status_message = f"Executing: {' '.join(cmd)}\n"
        print(status_message) # Log to console

        try:
            # Execute the script
            process = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=NODE_DIR) # cwd can be changed if scripts expect a specific one

            if process.stdout:
                status_message += f"Script STDOUT:\n{process.stdout}\n"
            if process.stderr:
                status_message += f"Script STDERR:\n{process.stderr}\n"
            
            if process.returncode == 0:
                status_message += f"Script '{selected_script}' executed successfully."
            else:
                status_message += f"Script '{selected_script}' failed with return code {process.returncode}."
            
        except FileNotFoundError:
            status_message = f"ERROR: Python interpreter '{interpreter_to_use}' or script '{script_full_path}' not found. Please check paths."
        except Exception as e:
            status_message = f"An unexpected error occurred while trying to run the script: {str(e)}"

        return (status_message,)

# --- Node Registration ---
NODE_CLASS_MAPPINGS = {
    "PortableScriptExecutor": PortableScriptExecutor
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "PortableScriptExecutor": "Portable Script Executor[自动数据]"
}

# Updated on: 2025-05-21 23:02:46

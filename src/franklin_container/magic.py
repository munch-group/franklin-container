from IPython.core.magic import register_line_magic
import subprocess
import shutil
import pyperclip
import webbrowser
from functools import wraps
import sys
import os
import tempfile

def crash_report(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            url = 'https://github.com/munch-group/franklin-container/issues'
            print(f"Error while running magic: {e}", file=sys.stderr)
            print("Please report this by creating an issue at:")
            print(url)
            print("The error description has been copied to your clipboard "
                   "for you to paste into the isue description.")
            pyperclip.copy(f"Exception occurred while running magic: {e}")
            webbrowser.open(url, new=1)
        return ret
    return wrapper

install_pixi_script = f'''
WORKSPACE_FOLDER="{os.getcwd()}"
ENVIRONMENT="prod"
export PIXI_HOME=/home/vscode
export PIXI_PROJECT_MANIFEST="$WORKSPACE_FOLDER/pixi.toml"
curl -fsSL https://pixi.sh/install.sh | bash
'''

@crash_report
def load_ipython_extension(ipython):
    """This function is called when `%load_ext franklin_container.magic` is run in IPython."""
    @register_line_magic
    def franklin(line):
        packages = line.strip().split()
        if not packages:
            print("Usage: %franklin <package-name> <package-name> ...")
            return
        
        if not shutil.which("pixi"):
            print("Installing pixi")
            script_file = tempfile.NamedTemporaryFile(mode='w')
            script_file.write(install_pixi_script)
            cmd = ["bash", script_file.name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode:
                print(f"Error installing {', '.join(packages)}':\n{result.stderr}")

        print(f"Installing: {', '.join(packages)}")
        pixi_exe = os.environ['PIXI_EXE']
        cmd = [pixi_exe, "add", "--feature", "exercise", "--platform", "linux-64"] + packages
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
#        print(f"Packages {', '.join(packages)} installed successfully.")
        # else:
        #     print(f"Error installing {', '.join(packages)}:\n{result.stderr}")


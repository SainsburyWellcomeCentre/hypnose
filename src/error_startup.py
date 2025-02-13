import subprocess
import os
from pathlib import Path

# ADD_FLAGS = "--no-editor" 
SAVE_LOG = True
log_dir = "logdir"
bonsai_path = r".bonsai/Bonsai.exe"
workflow_path = r"HypnoseMain.bonsai"
cwd = Path(__file__).parent.resolve()

output_cmd = f'"{bonsai_path}" "{workflow_path}"'

if SAVE_LOG:
    os.mkdir(log_dir)
    log = open(log_dir + "\\" + 'log.txt', 'a')  
    bonsai_process = subprocess.Popen(output_cmd, cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE, stdout=log, stderr=log)
else:
    bonsai_process = subprocess.Popen(output_cmd, cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE)
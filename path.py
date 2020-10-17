import sys
import os
import re
import subprocess
DIR_SCRIPT = sys.path[0]
print(DIR_SCRIPT)

REPLAYS_FOLDER = os.path.join(DIR_SCRIPT, 'replays')

print(REPLAYS_FOLDER)

files = [f for f in os.listdir(REPLAYS_FOLDER) if os.path.isfile(os.path.join(DIR_SCRIPT, REPLAYS_FOLDER, f))]
print(files)

print(os.path.join(DIR_SCRIPT, "capture.py"))

def generate_cmd(replay_path):
    file_name = os.path.basename(replay_path)
    match = re.search("(.*)_vs_(.*)_.*", file_name)
    red = "Red"
    blue = "Blue"
    if match and match.groups() and len(match.groups()) > 1:
        red, blue = match.groups()
    path1 = os.path.join(DIR_SCRIPT, "capture.py")
    path1 = '"' + path1 + '"' #.replace(" ", '\ ')
    replay_path =  '"' + replay_path + '"' #.replace(" ", '\ ')
    print(f'{"python"} {path1} --red-name {red} --blue-name {blue} --replay {replay_path} --delay-step {0}')
    return f'{"python"} {path1} --red-name {red} --blue-name {blue} --replay {replay_path} --delay-step {0}'

#print(os.path.join(DIR_SCRIPT, REPLAYS_FOLDER, files[0]))
os.system(generate_cmd(os.path.join(DIR_SCRIPT, REPLAYS_FOLDER, files[0])))   
#subprocess.run([generate_cmd(os.path.join(DIR_SCRIPT, REPLAYS_FOLDER, files[0]))])
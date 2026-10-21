
import time
from pathlib import Path
import subprocess
import sys

try:
    import pyautogui
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
    import pyautogui

pyautogui.FAILSAFE = False
CMD_FILE = Path.home() / "Downloads" / "ai_control_command.txt"
REPO = Path("C:/Users/Etern/Documents/roblox-scripting-demos")

def do(cmd_text):
    c = cmd_text.lower()
    print(f"Doing: {cmd_text}")
    if "portal" in c:
        be = REPO / "Blender_execute.py"
        if be.exists():
            subprocess.Popen([sys.executable, str(be)], cwd=str(REPO))
        (REPO / ".blender_trigger").write_text(str(time.time()))
    if "git" in c or "push" in c:
        subprocess.run("git add .", shell=True, cwd=REPO)
        subprocess.run('git commit -m "AI control"', shell=True, cwd=REPO)
        subprocess.run("git push", shell=True, cwd=REPO)
    if "click" in c and "import" in c:
        try:
            pyautogui.click(1000, 500)
        except:
            pass
    if "blender" in c and "open" in c:
        try:
            subprocess.Popen(["blender"], shell=True)
        except:
            pass

print("AI CONTROL ACTIVE - watching", CMD_FILE)
last = 0
while True:
    try:
        if CMD_FILE.exists():
            m = CMD_FILE.stat().st_mtime
            if m != last:
                last = m
                txt = CMD_FILE.read_text(encoding='utf-8', errors='ignore').strip()
                if txt:
                    CMD_FILE.unlink()
                    do(txt)
    except Exception as e:
        print(e)
    time.sleep(0.5)

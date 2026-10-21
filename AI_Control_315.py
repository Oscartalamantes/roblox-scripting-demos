
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

def execute(cmd_text):
    c = cmd_text.lower()
    print(f"AI executing: {cmd_text}")
    
    if "portal" in c:
        # Make portal at correct path
        import math
        verts=[]; faces=[]
        def torus(R,r,sm=28,sn=14):
            b=len(verts)
            for i in range(sm):
                th=2*math.pi*i/sm
                for j in range(sn):
                    ph=2*math.pi*j/sn
                    verts.append(((R+r*math.cos(ph))*math.cos(th),(R+r*math.cos(ph))*math.sin(th),r*math.sin(ph)))
            for i in range(sm):
                for j in range(sn):
                    a=b+i*sn+j; b1=b+((i+1)%sm)*sn+j; c=b+((i+1)%sm)*sn+(j+1)%sn; d=b+i*sn+(j+1)%sn
                    faces.append((a,b1,c,d))
        torus(2.0, 0.35)
        torus(1.6, 0.20)
        torus(1.2, 0.12)
        for out in [REPO / "assets" / "trophy" / "Labyrinth_Trophy_BIG.obj", REPO / "Labyrinth_Portal.obj"]:
            out.parent.mkdir(parents=True, exist_ok=True)
            with open(out,'w') as f:
                for v in verts:
                    f.write(f"v {v[0]} {v[1]} {v[2]}
")
                for fc in faces:
                    f.write(f"f {fc[0]+1} {fc[1]+1} {fc[2]+1} {fc[3]+1}
")
        (REPO / ".blender_trigger").write_text(str(time.time()))
        print("Portal made")
        # Push without oi-env
        subprocess.run("git add assets/trophy/Labyrinth_Trophy_BIG.obj Labyrinth_Portal.obj .gitignore", shell=True, cwd=REPO)
        subprocess.run('git commit -m "portal fix - no venv"', shell=True, cwd=REPO)
        subprocess.run("git push", shell=True, cwd=REPO)
        print("Pushed portal (no venv)")
        
        # Auto-click Import from Repo after 2 sec
        time.sleep(2)
        try:
            pyautogui.click(x=700, y=250)
            print("Auto-clicked Import from Repo")
        except Exception as e:
            print(f"Click failed: {e}")
    
    if "import" in c:
        try:
            pyautogui.click(x=700, y=250)
            print("Clicked Import from Repo")
        except Exception as e:
            print(e)

print(f"=== AI LAPTOP CONTROL ACTIVE (Python 3.15) ===")
print(f"Watching: {CMD_FILE}")
print("You type in Meta AI chat, I control mouse/keyboard here")
print("Commands: 'make portal', 'click import'")

last = 0
while True:
    try:
        if CMD_FILE.exists():
            mtime = CMD_FILE.stat().st_mtime
            if mtime != last:
                last = mtime
                text = CMD_FILE.read_text(encoding='utf-8', errors='ignore').strip()
                if text:
                    CMD_FILE.unlink(missing_ok=True)
                    execute(text)
    except Exception as e:
        print(e)
    time.sleep(0.5)

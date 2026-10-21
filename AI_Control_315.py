
import time
from pathlib import Path
import subprocess, sys
try:
    import pyautogui
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui", "--quiet"])
    import pyautogui
pyautogui.FAILSAFE = False
CMD_FILE = Path.home() / "Downloads" / "ai_control_command.txt"
REPO = Path("C:/Users/Etern/Documents/roblox-scripting-demos")
def execute(cmd_text):
    cmd = cmd_text.lower()
    print(f"Execute: {cmd_text}")
    if "portal" in cmd:
        import math
        verts=[]; faces=[]
        def torus(R,r,sm=24,sn=12):
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
        for out in [REPO / "assets" / "trophy" / "Labyrinth_Trophy_BIG.obj", REPO / "Labyrinth_Portal.obj"]:
            out.parent.mkdir(parents=True, exist_ok=True)
            with open(out,'w') as f:
                for v in verts: f.write(f"v {v[0]} {v[1]} {v[2]}
")
                for fc in faces: f.write(f"f {fc[0]+1} {fc[1]+1} {fc[2]+1} {fc[3]+1}
")
        (REPO / ".blender_trigger").write_text(str(time.time()))
        subprocess.run("git add .", shell=True, cwd=REPO)
        subprocess.run('git commit -m "AI control portal"', shell=True, cwd=REPO)
        subprocess.run("git push", shell=True, cwd=REPO)
        print("Portal made and pushed")
    if "import" in cmd:
        try:
            pyautogui.click(x=700, y=250)
            print("Clicked Import")
        except Exception as e:
            print(e)

print(f"AI CONTROL ACTIVE - watching {CMD_FILE}")
last = 0
while True:
    try:
        if CMD_FILE.exists():
            mtime = CMD_FILE.stat().st_mtime
            if mtime != last:
                last = mtime
                text = CMD_FILE.read_text(encoding='utf-8', errors='ignore').strip()
                if text:
                    CMD_FILE.unlink()
                    execute(text)
    except Exception as e:
        print(e)
    time.sleep(0.5)


import time
from pathlib import Path
import subprocess, sys
try:
    import pyautogui
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
    import pyautogui
pyautogui.FAILSAFE = False

REPO = Path("C:/Users/Etern/Documents/roblox-scripting-demos")
CMD_FILE = Path.home() / "Downloads" / "ai_control_command.txt"
LIVE_REQ = REPO / "LIVE_REQUEST.txt"

def execute(cmd_text):
    print(f"=== REQUEST FROM CHAT: {cmd_text} ===")
    LIVE_REQ.write_text(f"{time.strftime('%H:%M:%S')} - {cmd_text}", encoding='utf-8')
    
    # Trigger Blender auto-import via file, not mouse click - more reliable
    for p in [REPO / ".blender_trigger", Path.home() / "Downloads" / ".blender_trigger"]:
        try:
            p.write_text(str(time.time()))
        except: pass
    
    # Also rebuild OBJ immediately
    if "portal" in cmd_text.lower():
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
        torus(2.2, 0.35); torus(1.8, 0.22); torus(1.4, 0.15); torus(1.0, 0.10); torus(0.6, 0.06)
        for out in [REPO / "assets" / "trophy" / "Labyrinth_Trophy_BIG.obj", REPO / "Labyrinth_Portal.obj"]:
            out.parent.mkdir(parents=True, exist_ok=True)
            with open(out,'w') as f:
                for v in verts: f.write(f"v {v[0]} {v[1]} {v[2]}
")
                for fc in faces: f.write(f"f {fc[0]+1} {fc[1]+1} {fc[2]+1} {fc[3]+1}
")
        print(f"Portal rebuilt for request: {cmd_text}")
        (REPO / "LIVE_UPDATE.txt").write_text(f"LIVE {cmd_text} at {time.strftime('%H:%M:%S')} - {len(verts)} verts", encoding='utf-8')

print(f"=== AUTO PIPELINE ACTIVE ===")
print(f"Watching chat: {CMD_FILE}")
print("You type request -> I build -> Blender auto-imports LIVE - no old version")
print("Just see request and change - backend handled")

last=0
while True:
    try:
        if CMD_FILE.exists():
            m=CMD_FILE.stat().st_mtime
            if m!=last:
                last=m
                t=CMD_FILE.read_text(encoding='utf-8', errors='ignore').strip()
                if t:
                    CMD_FILE.unlink(missing_ok=True)
                    execute(t)
    except Exception as e:
        print(e)
    time.sleep(0.3)

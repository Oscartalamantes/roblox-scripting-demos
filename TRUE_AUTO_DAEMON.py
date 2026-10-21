import time
from pathlib import Path
import subprocess
import sys
import os

print("=== TRUE AUTOMATION DAEMON STARTING ===")
print(f"Python: {sys.executable}")
print(f"Version: {sys.version}")

REPO = Path("C:/Users/Etern/Documents/roblox-scripting-demos")
if not REPO.exists():
    REPO = Path(__file__).parent
    print(f"Using fallback REPO: {REPO}")

CMD_FILE = Path.home() / "Downloads" / "ai_control_command.txt"
LIVE_REQ = REPO / "LIVE_REQUEST.txt"
TRIGGER = REPO / ".blender_trigger"
DOWN_TRIGGER = Path.home() / "Downloads" / ".blender_trigger"

print(f"Watching: {CMD_FILE}")
print(f"Repo: {REPO}")

def build_portal(request_text):
    print(f"
=== BUILDING: {request_text} ===")
    try:
        LIVE_REQ.parent.mkdir(parents=True, exist_ok=True)
        LIVE_REQ.write_text(f"{time.strftime('%H:%M:%S')} - {request_text}", encoding='utf-8')
        
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
        
        torus(2.2, 0.35); torus(1.8, 0.22); torus(1.4, 0.15); torus(1.0, 0.10); torus(0.6, 0.06)
        
        for out in [REPO / "assets" / "trophy" / "Labyrinth_Trophy_BIG.obj", REPO / "Labyrinth_Portal.obj"]:
            try:
                out.parent.mkdir(parents=True, exist_ok=True)
                with open(out,'w') as f:
                    f.write(f"# AUTO {request_text} - {time.strftime('%H:%M:%S')}
")
                    for v in verts: f.write(f"v {v[0]} {v[1]} {v[2]}
")
                    for fc in faces: f.write(f"f {fc[0]+1} {fc[1]+1} {fc[2]+1} {fc[3]+1}
")
                print(f"Wrote {out}")
            except Exception as e:
                print(f"Write failed {out}: {e}")
        
        try:
            TRIGGER.write_text(str(time.time()))
            DOWN_TRIGGER.write_text(str(time.time()))
            (REPO / "LIVE_UPDATE.txt").write_text(f"LIVE {request_text} at {time.strftime('%H:%M:%S')} - {len(verts)} verts", encoding='utf-8')
            print(f"Triggers written - Blender will auto-delete old and build new")
        except Exception as e:
            print(f"Trigger failed: {e}")
        
        # Try git push but don't fail if not available
        try:
            subprocess.run("git add assets/trophy/Labyrinth_Trophy_BIG.obj LIVE_REQUEST.txt LIVE_UPDATE.txt", shell=True, cwd=REPO, timeout=5)
            subprocess.run(f'git commit -m "AUTO - {request_text[:50]}"', shell=True, cwd=REPO, timeout=5)
            subprocess.run("git push", shell=True, cwd=REPO, timeout=10)
            print("Pushed to GitHub")
        except Exception as e:
            print(f"Git push skipped: {e}")
        
        print(f"LIVE DONE - {request_text}")
        print("Open Blender to see live change - no old version")
    except Exception as e:
        print(f"BUILD FAILED: {e}")
        import traceback
        traceback.print_exc()

print("
Daemon active - leave this open")
print("Type in Meta AI chat: 'make portal'")
print("Or create file: Downloads/ai_control_command.txt with text 'make portal'")
print("")

last_cmd = 0
while True:
    try:
        if CMD_FILE.exists():
            mtime = CMD_FILE.stat().st_mtime
            if mtime != last_cmd:
                last_cmd = mtime
                text = CMD_FILE.read_text(encoding='utf-8', errors='ignore').strip()
                if text:
                    print(f"
Detected command file: {text}")
                    try:
                        CMD_FILE.unlink()
                    except: pass
                    build_portal(text)
    except Exception as e:
        print(f"Loop error: {e}")
    time.sleep(0.5)

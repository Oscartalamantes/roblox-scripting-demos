
import time, sys
from pathlib import Path
import subprocess, math, traceback

print("="*50)
print("TRUE AUTOMATION DAEMON - FIXED")
print("="*50)
print(f"Python: {sys.executable}")

REPO = Path("C:/Users/Etern/Documents/roblox-scripting-demos")
if not REPO.exists():
    REPO = Path(__file__).parent

CMD = Path.home() / "Downloads" / "ai_control_command.txt"
TRIG = REPO / ".blender_trigger"

print(f"Repo: {REPO}")
print(f"Watching: {CMD}")
print("")
print("DAEMON ACTIVE - LEAVE THIS WINDOW OPEN")
print("Type in chat: make portal")
print("")

def build(txt):
    print(f"
BUILD: {txt}")
    try:
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
        torus(2.2,0.35); torus(1.8,0.22); torus(1.4,0.15); torus(1.0,0.10); torus(0.6,0.06)
        for out in [REPO/"assets"/"trophy"/"Labyrinth_Trophy_BIG.obj", REPO/"Labyrinth_Portal.obj"]:
            out.parent.mkdir(parents=True, exist_ok=True)
            with open(out,'w') as f:
                for v in verts: f.write(f"v {v[0]} {v[1]} {v[2]}
")
                for fc in faces: f.write(f"f {fc[0]+1} {fc[1]+1} {fc[2]+1} {fc[3]+1}
")
        TRIG.write_text(str(time.time()))
        print(f"Wrote {len(verts)} verts - LIVE")
        try:
            subprocess.run("git add assets/trophy/Labyrinth_Trophy_BIG.obj Labyrinth_Portal.obj", shell=True, cwd=REPO, timeout=10)
            subprocess.run(f'git commit -m "AUTO {txt[:30]}"', shell=True, cwd=REPO, timeout=10)
            subprocess.run("git push", shell=True, cwd=REPO, timeout=15)
        except: pass
        print("DONE - LIVE in Blender")
    except Exception as e:
        print(f"FAILED: {e}")
        traceback.print_exc()

build("initial 5-ring portal")
last=0
while True:
    try:
        if CMD.exists():
            mtime=CMD.stat().st_mtime
            if mtime!=last:
                last=mtime
                t=CMD.read_text(encoding='utf-8', errors='ignore').strip()
                if t:
                    try: CMD.unlink()
                    except: pass
                    build(t)
    except Exception as e:
        print(e)
    time.sleep(0.5)


import time
from pathlib import Path
import subprocess, math
REPO=Path("C:/Users/Etern/Documents/roblox-scripting-demos")
CMD=Path.home()/"Downloads"/"ai_control_command.txt"
TRIG=REPO/".blender_trigger"
print("DAEMON ACTIVE - LEAVE OPEN - Type in chat: make portal")
def build(txt):
 print(f"BUILD: {txt}")
 verts=[]; faces=[]
 def torus(R,r):
  b=len(verts)
  for i in range(24):
   for j in range(12):
    th=2*3.14159*i/24; ph=2*3.14159*j/12
    verts.append(((R+r*math.cos(ph))*math.cos(th),(R+r*math.cos(ph))*math.sin(th),r*math.sin(ph)))
  for i in range(24):
   for j in range(12):
    a=b+i*12+j; b1=b+((i+1)%24)*12+j; c=b+((i+1)%24)*12+(j+1)%12; d=b+i*12+(j+1)%12
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
 try:
  subprocess.run("git add assets/trophy/Labyrinth_Trophy_BIG.obj Labyrinth_Portal.obj", shell=True, cwd=REPO, timeout=10)
  subprocess.run(f'git commit -m "AUTO {txt[:30]}"', shell=True, cwd=REPO, timeout=10)
  subprocess.run("git push", shell=True, cwd=REPO, timeout=15)
 except: pass
 print("DONE - LIVE")
build("initial")
last=0
while True:
 try:
  if CMD.exists():
   m=CMD.stat().st_mtime
   if m!=last:
    last=m
    t=CMD.read_text(encoding='utf-8', errors='ignore').strip()
    if t:
     try: CMD.unlink()
     except: pass
     build(t)
 except: pass
 time.sleep(0.5)

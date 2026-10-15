"""
File Bridge API v2 - For ZeroScript and Blender to talk
Same as before but hardened against locked files
"""
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, os, shutil, json, time
from pathlib import Path

app = FastAPI(title="Labyrinth Bridge API v2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

REPO = Path.home() / "Documents" / "roblox-scripting-demos"

@app.get("/")
def root():
    return {
        "status": "Labyrinth Bridge Online v2",
        "repo": str(REPO),
        "is_git": (REPO / ".git").exists(),
        "docs": "/docs",
        "endpoints": ["/upload", "/status", "/manifest"]
    }

@app.get("/status")
def status():
    manifest = REPO / "assets" / "sync_manifest.json"
    data = {}
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text())
        except:
            pass
    # List trophies
    trophy_dir = REPO / "assets" / "trophy"
    trophies = []
    if trophy_dir.exists():
        trophies = [p.name for p in trophy_dir.glob("*.obj")]
    return {
        "repo_exists": REPO.exists(),
        "is_git_repo": (REPO / ".git").exists(),
        "trophies": trophies,
        "manifest": data,
        "time": time.time()
    }

@app.get("/manifest")
def get_manifest():
    p = REPO / "assets" / "sync_manifest.json"
    if p.exists():
        return json.loads(p.read_text())
    return {}

@app.post("/upload")
async def upload(file: UploadFile = File(...), path: str = "assets/trophy"):
    dest_dir = REPO / path
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / file.filename
    # Avoid lock by writing to temp then rename
    tmp = dest_dir / f".{file.filename}.tmp"
    with open(tmp, "wb") as f:
        shutil.copyfileobj(file.file, f)
    if dest.exists():
        dest.unlink()
    tmp.rename(dest)
    return {"saved": str(dest), "size": dest.stat().st_size}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

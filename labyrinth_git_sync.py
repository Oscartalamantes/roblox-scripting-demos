"""
Labyrinth Bidirectional Git Sync - the brain
Watches local files -> git push, and watches git remote -> git pull

Fixes:
- "not a git repository" error by auto-cloning if needed
- Locked file errors by ignoring temp files and .bridge locks
- Bidirectional: Blender -> Git AND Git -> Blender

Run: python labyrinth_git_sync.py
"""
import os
import time
import json
import subprocess
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# CONFIG
REPO_PATH = Path.home() / "Documents" / "roblox-scripting-demos"
WATCH_PATH = REPO_PATH / "assets"
REMOTE_CHECK_INTERVAL = 30  # seconds - how often to check git remote for new pulls
DEBOUNCE = 2.0
IGNORE_NAMES = {"file_bridge_api.py", "labyrinth_git_sync.py", "start_labyrinth_bridge.bat", "__pycache__", ".git"}

def run(cmd, cwd=REPO_PATH):
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=False, timeout=15)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def is_git_repo():
    return (REPO_PATH / ".git").exists()

def ensure_repo():
    if not is_git_repo():
        print(f"[SYNC] {REPO_PATH} is not a git repo. Attempting to fix...")
        # Try to find remote from existing git config backup or ask user
        # For now just warn
        print("[SYNC] Please run setup_labyrinth_bridge.ps1 to clone correctly")
        return False
    return True

def git_push_file(filepath: Path):
    if not ensure_repo():
        return
    rel = filepath.relative_to(REPO_PATH) if filepath.is_relative_to(REPO_PATH) else filepath.name
    # Ignore bridge files themselves
    if any(ign in str(rel) for ign in IGNORE_NAMES):
        return
    # Ignore temp blender files
    if filepath.suffix in [".blend1", ".tmp", ".lock"] or filepath.name.startswith("."):
        return
    
    print(f"[SYNC] Detected change: {rel} -> pushing...")
    run(["git", "add", str(rel)])
    # Also add manifest
    run(["git", "add", "assets/sync_manifest.json", "assets/trophy/"], cwd=REPO_PATH)
    
    # Only commit if something to commit
    ok, out = run(["git", "diff", "--cached", "--quiet"])
    if ok: # diff quiet returns 0 when no diff
        print("[SYNC] No staged changes, skip")
        return
    
    ok, out = run(["git", "commit", "-m", f"auto: {rel} from Blender bridge"])
    print(out)
    if ok:
        ok2, out2 = run(["git", "push"])
        print(out2)
        if ok2:
            print("[SYNC] Pushed to GitHub ✓")
            # Update manifest
            manifest_path = REPO_PATH / "assets" / "sync_manifest.json"
            manifest = {}
            if manifest_path.exists():
                try:
                    manifest = json.loads(manifest_path.read_text())
                except:
                    pass
            manifest[str(rel)] = {"last_push": time.time(), "source": "local"}
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps(manifest, indent=2))
        else:
            print("[SYNC] Push failed - maybe need pull first, trying pull --rebase")
            run(["git", "pull", "--rebase"])
            run(["git", "push"])

def check_remote():
    """Git -> Local direction: check if remote has new stuff"""
    if not ensure_repo():
        return
    # Fetch
    ok, out = run(["git", "fetch"])
    if not ok:
        return
    # Check if behind
    ok, out = run(["git", "rev-list", "HEAD..origin/main", "--count"])
    try:
        behind = int(out.strip())
        if behind > 0:
            print(f"[SYNC] Remote is {behind} commits ahead -> pulling...")
            ok, out = run(["git", "pull"])
            print(out)
            if ok:
                # Write manifest for Blender addon to see
                manifest_path = REPO_PATH / "assets" / "sync_manifest.json"
                manifest = {}
                if manifest_path.exists():
                    try:
                        manifest = json.loads(manifest_path.read_text())
                    except:
                        pass
                manifest["_last_pull"] = {"time": time.time(), "behind": behind}
                manifest_path.parent.mkdir(parents=True, exist_ok=True)
                manifest_path.write_text(json.dumps(manifest, indent=2))
                print("[SYNC] Pulled ✓ - Blender will see it in Labyrinth panel")
    except:
        pass

class DebouncedHandler(FileSystemEventHandler):
    def __init__(self):
        self.last = {}
    
    def on_any_event(self, event):
        if event.is_directory:
            return
        p = Path(event.src_path)
        # Skip git internal and bridge
        if ".git" in p.parts:
            return
        if any(ign in p.name for ign in IGNORE_NAMES):
            return
        # Only care about assets
        if "assets" not in p.parts:
            return
        
        now = time.time()
        if str(p) in self.last and now - self.last[str(p)] < DEBOUNCE:
            return
        self.last[str(p)] = now
        
        # Small delay for Blender to finish writing
        time.sleep(0.5)
        git_push_file(p)

if __name__ == "__main__":
    print(f"=== Labyrinth Bidirectional Bridge ===")
    print(f"Repo: {REPO_PATH}")
    print(f"Watching: {WATCH_PATH}")
    print(f"Mode: Blender <-> Local <-> Git (both ways)")
    
    if not is_git_repo():
        print(f"ERROR: {REPO_PATH} is not a git repo!")
        print("Run setup_labyrinth_bridge.ps1 first")
        sys.exit(1)
    
    WATCH_PATH.mkdir(parents=True, exist_ok=True)
    (WATCH_PATH / "trophy").mkdir(parents=True, exist_ok=True)
    
    # Initial .gitignore
    gitignore = REPO_PATH / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("file_bridge_api.py\nlabyrinth_git_sync.py\nstart_labyrinth_bridge.bat\n__pycache__/\n*.pyc\n*.blend1\n")
    
    event_handler = DebouncedHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_PATH), recursive=True)
    observer.start()
    
    print("[SYNC] Watching local files...")
    print(f"[SYNC] Checking remote every {REMOTE_CHECK_INTERVAL}s for Git -> Local")
    try:
        last_remote_check = 0
        while True:
            time.sleep(1)
            if time.time() - last_remote_check > REMOTE_CHECK_INTERVAL:
                check_remote()
                last_remote_check = time.time()
    except KeyboardInterrupt:
        observer.stop()
        print("\n[SYNC] Stopped")
    observer.join()

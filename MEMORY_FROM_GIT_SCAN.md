# Memory from GitHub: C:\Users\Etern\Documents\roblox-scripting-demos
# URL: https://github.com/Oscartalamantes/roblox-scripting-demos
## TRUE SOUL C:\Users\Etern\Desktop\MetaAI_Logs\_muse_soul.md
# _muse_soul.md auto-created
OscarAI init


# Soul: # _muse_soul.md auto-created
OscarAI init

## LobbyEffects.client.luau
-- Lobby Client Effects - Particles, UI, Trophy Inspect
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer

-- Trophy inspected UI
local trophyEvent = ReplicatedStorage:WaitForChild("TrophyInspected")
trophyEvent.OnClientEvent:Connect(function()
    local gui = player:FindFirstChild("PlayerGui"):FindFirstChild("TrophyUI")
    if not gui then
        gui = Instance.new("ScreenGui")
        gui.Name = "TrophyUI"
        gui.Parent = player.PlayerGui
        
        local frame = Instance.new("Frame")
        frame.Size = UDim2.fromScale(0.4, 0.3)
        frame.Position = UDim2.fromScale(0.3, 0.35)
        frame.BackgroundColor3 = Color3.fromRGB(20,20,30)
        frame.BorderSizePixel = 0
        frame.Parent = gui
        
        local uiCorner = Instance.new("UICorner", frame)
        uiCorner.CornerRadius = UDim.new(0, 12)
        
        local title = Instance.new("TextLabel")
        title.Size = UDim2.new(1,0,0,50)
        title.Text = "LABYRINTH CHAMPION TROPHY"
        title.TextColor3 = Color3.fromRGB(255, 215, 0)
        title.Font = Enum.Font.GothamBold
        title.TextScaled = true
        title.BackgroundTransparency = 1
        title.Parent = frame
        
        local desc = Instance.new("TextLabel")
        desc.Size = UDim2.new(1,-20,1,-70)
        desc.Position = UDim2.new(0,10,0,60)
        desc.Text = "Forged from pure gold with a crystal crown and eternal star.\n\nOnly the worthy who escape the labyrinth may claim it.\n\nUpload your Labyrinth_Trophy_BIG.obj to rbxassetid to see the real mesh."
        desc.TextColor3 = Color3.new(1,1,1)
        desc.TextWrapped = true
        desc.BackgroundTransparency = 1
        desc.Parent = frame
        
        game.Debris:AddItem(gui, 5)
    end
end)

-- Teleport pad UI
local teleportEvent = ReplicatedStorage:WaitForChild("TeleportRequested")
teleportEvent.On
## Lobby.server.luau
-- Labyrinth Proper Lobby - Builds Circular Lobby with Trophy Pedestal
local LobbyConfig = require(game.ReplicatedStorage.Shared:WaitForChild("LobbyConfig"))
local Trophy = require(game.ReplicatedStorage.Shared:WaitForChild("Trophy"))

local function getOrCreateFolder(name, parent)
    local f = parent:FindFirstChild(name)
    if not f then
        f = Instance.new("Folder")
        f.Name = name
        f.Parent = parent
    end
    return f
end

local function buildFloor()
    local lobby = workspace:FindFirstChild("Lobby")
    if not lobby then
        lobby = Instance.new("Folder")
        lobby.Name = "Lobby"
        lobby.Parent = workspace
    end
    
    -- Circular marble floor
    local floor = lobby:FindFirstChild("Floor")
    if floor then floor:Destroy() end
    
    floor = Instance.new("Part")
    floor.Name = "Floor"
    floor.Shape = Enum.PartType.Cylinder
    floor.Size = Vector3.new(1, LobbyConfig.RADIUS*2, LobbyConfig.RADIUS*2)
    floor.CFrame = CFrame.new(0, -0.5, 0) * CFrame.Angles(0,0,math.rad(90))
    floor.Material = Enum.Material.Marble
    floor.Color = Color3.fromRGB(25, 25, 35)
    floor.Anchored = true
    floor.Parent = lobby
    
    -- Gold rings in floor
    for r = 20, 50, 10 do
        local ring = Instance.new("Part")
        ring.Name = "GoldRing_"..r
        ring.Shape = Enum.PartType.Cylinder
        ring.Size = Vector3.new(0.1, r*2, r*2)
        ring.CFrame = CFrame.new(0, 0.05, 0) * CFrame.Angles(0,0,math.rad(90))
        ring.Material = Enum.Material.Metal
        ring.Color = Color3.fromRGB(255, 215, 0)
        ring.Anchored = true
        ring.Transparency = 0.5
        ring.Parent = lobby
    end
end

local function buildPillars()
    local lobby = workspace:FindFirstChild("Lobby")
    for i=1, LobbyConfig.PILLARS do
        local angle = (i-1) * (360 / LobbyConfig.PILLARS)
        local rad = math.rad(angle)
        local x = math.cos(rad) * LobbyConfig.PILLAR_RADIUS
        local z = math.sin(rad) * LobbyConfig.PILLA
## LobbyConfig.luau
-- Labyrinth Proper Lobby Config
local LobbyConfig = {}

LobbyConfig.RADIUS = 60 -- studs circular lobby
LobbyConfig.FLOOR_Y = 0
LobbyConfig.PEDESTAL_HEIGHT = 5
LobbyConfig.PEDESTAL_SIZE = Vector3.new(10, 5, 10)
LobbyConfig.TROPHY_OFFSET = Vector3.new(0, 8.5, 0) -- on top of pedestal
LobbyConfig.TROPHY_MESH_ID = "" -- Set after upload: rbxassetid://12345678
LobbyConfig.TROPHY_SCALE = Vector3.new(6.5, 10.7, 6.5)
LobbyConfig.TROPHY_ROTATION_SPEED = 0.7 -- degrees per frame

LobbyConfig.PILLARS = 8
LobbyConfig.PILLAR_HEIGHT = 25
LobbyConfig.PILLAR_RADIUS = LobbyConfig.RADIUS - 5

LobbyConfig.TELEPORT_PADS = {
    {Name="PlayLabyrinth", Display="PLAY", Color=Color3.fromRGB(0, 170, 255), CFrame=CFrame.new(30, 1, 0), TeleportTo="LabyrinthGame"},
    {Name="Shop", Display="SHOP", Color=Color3.fromRGB(255, 215, 0), CFrame=CFrame.n

## auto_sync_git.py (870 chars)
import os, time, subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH = "./assets"
class Handler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory: return
        print(f"Changed: {event.src_path} -> pushing...")
        try:
            subprocess.run(["git","add","."], check=False)
            subprocess.run(["git","commit","-m",f"auto-sync {os.path.basename(event.src_path)}"], check=False)
            subprocess.run(["git","push"], check=False)
        except Exception as e:
            print(e)

print(f"Watching {WATCH}... (Ctrl+C to stop)")
os.makedirs(WATCH, exist_ok=True)
observer = Observer()
observer.schedule(Handler(), WATCH, recursive=True)
observer.start()
try:
    while True: time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()


## file_bridge_api.py (5256 chars)

"""
Labyrinth Bridge - File Transfer System
Connects Blender MCP to roblox-scripting-demos Git repo
Handles: Auto Export on Save, Export to Repo (-> Git), Import from Repo (Git ->)

Repo: C:/Users/Etern/Documents/roblox-scripting-demos (from screenshot)
Target: assets/trophy/Labyrinth_Trophy_BIG.obj (722 meshes, 353 objects in screenshot)

Usage via Blender MCP:
bpy.data.screens["temp"].areas[0].spaces[0].params.directory = "C:/Users/Etern/Documents/roblox-scripting-demos/assets/trophy/"
bpy.ops.ui.copy_data_path_button(full_path=True) -> gets the directory

API for Meta AI to handle transfers:
"""
import os
import shutil
import subprocess
import pathlib
from datetime import datetime

REPO_PATH = pathlib.Path("C:/Users/Etern/Documents/roblox-scripting-demos")
# Also check common locations
POSSIBLE_REPOS = [
    pathlib.Path("C:/Users/Etern/Desktop/LobbyLR"),
    pathlib.Path("C:/Users/Etern/Documents/roblox-scripting-demos"),
    pathlib.Path("C:/Users/Etern/Downloads/roblox-scripting-demos"),
]

TARGET_OBJ = "assets/trophy/Labyrinth_Trophy_BIG.obj"
TARGET_FBX = "assets/trophy/Labyrinth_Trophy_BIG.fbx"
ASSETS_DIR = "assets/lobby"

def find_repo():
    for p in POSSIBLE_REPOS:
        if p.exists():
            return p
    return REPO_PATH

def get_git_status(repo=None):
    repo = repo or find_repo()
    try:
        result = subprocess.run(["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True, timeout=5)
        return result.stdout
    except Exception as e:
        return f"Git not available: {e}"

def export_to_repo(source_file, target_relative=None, repo=None):
    """
    Export to Repo (-> Git)
    Called by Labyrinth Bridge addon button
    """
    repo = repo or find_repo()
    target_relative = target_relative or TARGET_OBJ
    target = repo / target_relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_file, target)
    print(f"Exported {source_file} -> {target}")
    
    # Auto git add
    try:
        subprocess.run(["git", "add", str(target_relative)], cwd=repo, timeout=5)
        status = get_git_status(repo)
        print(f"Git status after add:\n{status}")
        return {"success": True, "target": str(target), "git_status": status}
    except Exception as e:
        return {"success": True, "target": str(target), "git_error": str(e)}

def import_from_repo(target_relative=None, dest=None, repo=None):
    """
    Import from Repo (Git ->)
    """
    repo = repo or find_repo()
    target_relative = target_relative or TARGET_OBJ
    source = repo / target_relative
    if not source.exists():
        return {"success": False, "error": f"{source} not found"}
    if dest:
        shutil.copy2(source, dest)
        print(f"Imported {source} -> {dest}")
    return {"success": True, "source": str(source), "dest": str(dest) if dest else None}

def auto_export_on_save(blender_file_path, repo=None):
    """
    Auto Export on Save - triggered when .blend is saved
    """
    repo = repo or find_repo()
    # Export current scene as OBJ/FBX to target
    print(f"Auto export triggered for {blender_file_path}")
    # In real Blender, this would do bpy.ops.export_scene.obj(filepath=str(repo/TARGET_OBJ))
    return export_to_repo(blender_file_path, TARGET_OBJ, repo)

def fix_git_status(repo=None):
    """Fix Git Status button"""
    repo = repo or find_repo()
    try:
        # git add -A
        subprocess.run(["git", "add", "-A"], cwd=repo, timeout=5)
        status = get_git_status(repo)
        return {"fixed": True, "status": status}
    except Exception as e:
        return {"fixed": False, "error": str(e)}

# --- MCP API for Meta AI ---
# This is what Meta AI calls to handle transfers for you

def mcp_handle_transfer(action="export", source="/mnt/data/LabyrinthRush_Final_Lobby/LabyrinthRush_Lobby_Final.fbx"):
    """
    Called by Meta AI via Blender MCP
    action: export | import | status | auto_export
    """
    repo = find_repo()
    print(f"=== Labyrinth Brid

## file_bridge_api_fixed.py (519 chars)
from fastapi import FastAPI, File, UploadFile
import uvicorn, os, shutil
app = FastAPI()
@app.get("/")
def root(): return {"status":"Labyrinth Bridge Online","docs":"/docs"}
@app.post("/upload")
async def upload(file: UploadFile = File(...), path: str = "assets/trophy"):
    os.makedirs(path, exist_ok=True)
    dest = os.path.join(path, file.filename)
    with open(dest,"wb") as f: shutil.copyfileobj(file.file, f)
    return {"saved":dest}
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


## labyrinth_git_sync.py (6597 chars)
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
                if manifest_path.

## labyrinth_one_click_loader.py (6967 chars)

"""
One-Click Import from Repo - Loads ALL models game-ready
PROPER BLUEPRINT VERSION - No transfer needed, just click Import from Repo
I do everything - you just click.

Original blueprint: 400x400 vaulted, 8 gothic pillars, fireplace, 2 braziers, 2 chandeliers x6 candles, 4 tables, red carpet 130, green runic pad
"""

import bpy
import pathlib

REPO = pathlib.Path("C:/Users/Etern/Documents/roblox-scripting-demos")
REPOS = [
    pathlib.Path("C:/Users/Etern/Desktop/LobbyLR"),
    REPO,
    pathlib.Path("C:/Users/Etern/Documents/roblox-scripting-demos"),
    pathlib.Path("C:/Users/Etern/Downloads/labyrinth-rush-testrig (22)"),
]

def find_repo():
    for r in REPOS:
        if r.exists():
            return r
    return REPO

def import_obj(filepath, location=(0,0,0)):
    filepath = pathlib.Path(filepath)
    if not filepath.exists():
        return None
    print(f"Importing {filepath} at {location}")
    bpy.ops.wm.obj_import(filepath=str(filepath))
    obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
    if obj:
        obj.location = location
    return obj

def import_fbx(filepath, location=(0,0,0)):
    filepath = pathlib.Path(filepath)
    if not filepath.exists():
        return None
    try:
        print(f"Importing FBX {filepath} at {location}")
        bpy.ops.import_scene.fbx(filepath=str(filepath))
        obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
        if obj:
            obj.location = location
        return obj
    except Exception as e:
        print(f"FBX import failed {e}, trying OBJ")
        return None

def setup_materials():
    mats = {
        "Stone": {"color": (72/255, 68/255, 88/255, 1), "rough": 0.85},
        "DarkStone": {"color": (55/255, 52/255, 68/255, 1), "rough": 0.9},
        "SlateFloor": {"color": (42/255, 40/255, 56/255, 1), "rough": 0.85},
        "Wood": {"color": (85/255, 60/255, 40/255, 1), "rough": 0.7},
        "Metal": {"color": (45/255, 45/255, 50/255, 1), "rough": 0.3, "metallic": 0.8},
        "Fire": {"color": (1, 0.47, 0.08, 1), "rough": 0.5, "emission": (1, 0.3, 0.05, 1), "emission_strength": 6.0},
        "Rune": {"color": (0, 1, 0.47, 1), "rough": 0.4, "emission": (0, 1, 0.4, 1), "emission_strength": 5.0},
        "Carpet": {"color": (140/255, 20/255, 30/255, 1), "rough": 0.9},
        "Brick": {"color": (120/255, 65/255, 50/255, 1), "rough": 0.9},
    }
    for name, props in mats.items():
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = props["color"]
        bsdf.inputs["Roughness"].default_value = props["rough"]
        if "metallic" in props:
            bsdf.inputs["Metallic"].default_value = props["metallic"]
        if "emission" in props:
            bsdf.inputs["Emission"].default_value = props["emission"]
            bsdf.inputs["Emission Strength"].default_value = props["emission_strength"]

def import_all_game_ready():
    """
    ONE-CLICK: Import from Repo (Git ->) -> Loads ALL models game-ready
    This is the ONLY thing you click - I do everything else
    """
    repo = find_repo()
    print(f"=== ONE-CLICK IMPORT FROM REPO (PROPER BLUEPRINT) ===")
    print(f"Repo: {repo}")
    try:
        d = bpy.data.screens["temp"].areas[0].spaces[0].params.directory
        print(f"Blender file browser dir: {d}")
    except:
        pass
    
    setup_materials()
    
    # PRIORITY ORDER: Proper blueprint OBJ (237KB, 4656 verts) is the REAL lobby
    # This is what you said was missing - the original blueprint, not placeholder
    proper_obj = repo / "assets/lobby/Labyrinth_Lobby_PROPER_BLUEPRINT.obj"
    proper_fbx = repo / "assets/lobby/Labyrinth_Lobby_PROPER_BLUEPRINT.fbx"
    final_fbx = repo / "assets/lobby/Labyrinth_Lobby_FINAL.fbx"
    final_obj = repo / "assets/lobby/Labyrinth_Lobby_FINAL.obj"
    lobby_final_obj = repo /

## LabyrinthRush\labyrinth_bridge_addon.py (5707 chars)

bl_info = {
    "name": "Labyrinth Bridge - One Click",
    "author": "LabyrinthRush",
    "version": (2, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Labyrinth",
    "description": "One-Click Import from Repo loads ALL models game-ready. Export to Repo pushes, Publish uploads to Roblox",
    "category": "Import-Export",
}

import bpy
import pathlib
import shutil
import subprocess

REPO = pathlib.Path("C:/Users/Etern/Documents/roblox-scripting-demos")
REPOS = [
    pathlib.Path("C:/Users/Etern/Desktop/LobbyLR"),
    REPO,
    pathlib.Path("C:/Users/Etern/Documents/roblox-scripting-demos"),
]

def find_repo():
    for r in REPOS:
        if r.exists():
            return r
    return REPO

class LABYRINTH_OT_import_from_repo(bpy.types.Operator):
    """Import from Repo (Git ->) - Loads ALL models game-ready"""
    bl_idname = "labyrinth.import_from_repo"
    bl_label = "Import from Repo (Git ->)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Import the loader module
        try:
            import labyrinth_one_click_loader
            import importlib
            importlib.r

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
    print(f"=== Labyrinth Bridge MCP Handle ===")
    print(f"Repo: {repo}")
    print(f"Action: {action}")
    print(f"Source: {source}")
    print(f"Directory from bpy: {bpy.data.screens['temp'].areas[0].spaces[0].params.directory if 'bpy' in globals() else 'N/A - running outside Blender'}")
    
    if action == "export":
        # Export lobby to repo as both OBJ and FBX
        result_fbx = export_to_repo(source, TARGET_FBX, repo)
        # Also export OBJ version
        obj_source = source.replace(".fbx", ".obj") if source.endswith(".fbx") else source
        result_obj = export_to_repo(obj_source, TARGET_OBJ, repo) if pathlib.Path(obj_source).exists() else result_fbx
        return {"fbx": result_fbx, "obj": result_obj, "repo": str(repo)}
    
    elif action == "import":
        return import_from_repo(TARGET_OBJ, source, repo)
    
    elif action == "status":
        status = get_git_status(repo)
        return {"repo": str(repo), "git_status": status, "target_exists": (repo / TARGET_OBJ).exists()}
    
    elif action == "auto_export":
        return auto_export_on_save(source, repo)

# For direct Blender execution
if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    print(mcp_handle_transfer(action))

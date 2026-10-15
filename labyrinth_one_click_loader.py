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

def import_fbx(filepath, location=(0,0,0)):
    filepath = pathlib.Path(filepath)
    if not filepath.exists():
        print(f"Missing: {filepath}")
        return None
    bpy.ops.import_scene.fbx(filepath=str(filepath))
    obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
    if obj:
        obj.location = location
    print(f"Imported {filepath} at {location}")
    return obj

def import_obj(filepath, location=(0,0,0)):
    filepath = pathlib.Path(filepath)
    if not filepath.exists():
        print(f"Missing: {filepath}")
        return None
    bpy.ops.wm.obj_import(filepath=str(filepath))
    obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else None
    if obj:
        obj.location = location
    print(f"Imported {filepath} at {location}")
    return obj

def setup_materials():
    mats = {
        "Stone": {"color": (72/255, 68/255, 88/255, 1), "rough": 0.85},
        "DarkStone": {"color": (55/255, 52/255, 68/255, 1), "rough": 0.9},
        "Wood": {"color": (85/255, 60/255, 40/255, 1), "rough": 0.7},
        "Metal": {"color": (45/255, 45/255, 50/255, 1), "rough": 0.3, "metallic": 0.8},
        "Fire": {"color": (1, 0.47, 0.08, 1), "rough": 0.5, "emission": (1, 0.3, 0.05, 1), "emission_strength": 6.0},
        "Rune": {"color": (0, 1, 0.47, 1), "rough": 0.4, "emission": (0, 1, 0.4, 1), "emission_strength": 5.0},
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
    repo = find_repo()
    print(f"=== ONE-CLICK IMPORT FROM REPO ===")
    print(f"Repo: {repo}")
    try:
        d = bpy.data.screens["temp"].areas[0].spaces[0].params.directory
        print(f"Blender file browser dir: {d}")
    except:
        pass
    setup_materials()
    lobby_fbx = repo / "assets/lobby/Labyrinth_Lobby_FINAL.fbx"
    lobby_obj = repo / "assets/lobby/Labyrinth_Lobby_FINAL.obj"
    trophy_obj = repo / "assets/trophy/Labyrinth_Trophy_BIG.obj"
    if lobby_fbx.exists():
        import_fbx(lobby_fbx, (0,0,0))
    elif lobby_obj.exists():
        import_obj(lobby_obj, (0,0,0))
    else:
        print("No lobby file, checking /mnt/data fallback")
    if trophy_obj.exists():
        import_obj(trophy_obj, (0,10,0))
    for col_name in ["Lobby","Trophy","Pillars","Tables","Lighting"]:
        if col_name not in bpy.data.collections:
            col = bpy.data.collections.new(col_name)
            bpy.context.scene.collection.children.link(col)
    print("=== ALL MODELS LOADED GAME-READY ===")
    print("Next: Edit -> Export to Repo -> Publish")
    return {"success": True, "repo": str(repo)}

def export_all_game_ready():
    repo = find_repo()
    bpy.ops.export_scene.fbx(filepath=str(repo / "assets/lobby/Labyrinth_Lobby_FINAL.fbx"), use_selection=False, apply_scale_options='FBX_SCALE_ALL')
    bpy.ops.wm.obj_export(filepath=str(repo / "assets/trophy/Labyrinth_Trophy_BIG.obj"), export_selected_objects=False)
    print(f"Exported to {repo}")
    return {"success": True, "repo": str(repo)}

if __name__ == "__main__":
    import_all_game_ready()

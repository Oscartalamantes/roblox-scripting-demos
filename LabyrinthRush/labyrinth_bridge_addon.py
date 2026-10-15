
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
            importlib.reload(labyrinth_one_click_loader)
            result = labyrinth_one_click_loader.import_all_game_ready()
            self.report({'INFO'}, f"Loaded all models from {result['repo']}")
        except Exception as e:
            self.report({'ERROR'}, f"Import failed: {e}")
            import traceback
            traceback.print_exc()
        return {'FINISHED'}

class LABYRINTH_OT_export_to_repo(bpy.types.Operator):
    """Export to Repo (-> Git) - Pushes edits to Git"""
    bl_idname = "labyrinth.export_to_repo"
    bl_label = "Export to Repo (-> Git)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            import labyrinth_one_click_loader
            import importlib
            importlib.reload(labyrinth_one_click_loader)
            result = labyrinth_one_click_loader.export_all_game_ready()
            # Git add
            repo = find_repo()
            subprocess.run(["git", "add", "assets/"], cwd=repo, timeout=5)
            status = subprocess.run(["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True, timeout=5).stdout
            self.report({'INFO'}, f"Exported to {repo}, Git: {status[:100]}")
        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {e}")
        return {'FINISHED'}

class LABYRINTH_OT_publish(bpy.types.Operator):
    """Publish - Uploads to Roblox game"""
    bl_idname = "labyrinth.publish"
    bl_label = "Publish to Game"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        repo = find_repo()
        # Copy FBX to publish folder
        publish_dir = repo / "publish"
        publish_dir.mkdir(exist_ok=True)
        src = repo / "assets/lobby/Labyrinth_Lobby_FINAL.fbx"
        if src.exists():
            shutil.copy2(src, publish_dir / "Lobby_FINAL_PUBLISH.fbx")
            self.report({'INFO'}, f"Published {src} to {publish_dir} - Ready for Roblox Studio import at 0,76,5000")
        return {'FINISHED'}

class LABYRINTH_PT_panel(bpy.types.Panel):
    bl_label = "Labyrinth Bridge"
    bl_idname = "LABYRINTH_PT_bridge"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Labyrinth'
    
    def draw(self, context):
        layout = self.layout
        repo = find_repo()
        layout.label(text=f"Repo: {repo}")
        
        # Get Blender file browser dir like user showed
        try:
            d = bpy.data.screens["temp"].areas[0].spaces[0].params.directory
            layout.label(text=f"Blender Dir: {d}", icon='FILE_FOLDER')
        except:
            layout.label(text="Blender Dir: (MCP)", icon='FILE_FOLDER')
        
        layout.prop(context.scene, "labyrinth_repo_path", text="Repo Pa..")
        layout.prop(context.scene, "labyrinth_auto_export", text="Auto Export on Save")
        
        row = layout.row()
        row.operator("labyrinth.export_to_repo", icon='EXPORT')
        row = layout.row()
        row.operator("labyrinth.import_from_repo", icon='IMPORT')
        
        layout.separator()
        layout.label(text="Target: Labyrinth_Trophy_BIG.obj")
        layout.label(text="Target: Labyrinth_Lobby_FINAL.fbx")
        
        try:
            status = subprocess.run(["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True, timeout=3).stdout
            if status:
                layout.label(text="Git changes detected:", icon='ERROR')
                layout.label(text=status[:200])
            else:
                layout.label(text="Git clean", icon='CHECKMARK')
        except:
            layout.label(text="Git status unknown")
        
        layout.separator()
        layout.operator("labyrinth.publish", icon='CHECKMARK', text="Publish to Game")

def register():
    bpy.types.Scene.labyrinth_repo_path = bpy.props.StringProperty(name="Repo Path", default=str(REPO))
    bpy.types.Scene.labyrinth_auto_export = bpy.props.BoolProperty(name="Auto Export on Save", default=True)
    bpy.utils.register_class(LABYRINTH_OT_import_from_repo)
    bpy.utils.register_class(LABYRINTH_OT_export_to_repo)
    bpy.utils.register_class(LABYRINTH_OT_publish)
    bpy.utils.register_class(LABYRINTH_PT_panel)

def unregister():
    bpy.utils.unregister_class(LABYRINTH_PT_panel)
    bpy.utils.unregister_class(LABYRINTH_OT_publish)
    bpy.utils.unregister_class(LABYRINTH_OT_export_to_repo)
    bpy.utils.unregister_class(LABYRINTH_OT_import_from_repo)
    del bpy.types.Scene.labyrinth_repo_path
    del bpy.types.Scene.labyrinth_auto_export

if __name__ == "__main__":
    register()

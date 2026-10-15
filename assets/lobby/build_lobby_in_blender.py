
import bpy
import math, os
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
RADIUS = 60
PILLARS = 8
PILLAR_RADIUS = RADIUS - 5
bpy.ops.mesh.primitive_cylinder_add(radius=RADIUS, depth=1, location=(0,0,0))
floor = bpy.context.active_object
floor.name = "Lobby_Floor"
for r in [20,30,40,50]:
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.15, location=(0,0,0.05))
    ring = bpy.context.active_object
    ring.name = f"GoldRing_{r}"
bpy.ops.mesh.primitive_cylinder_add(radius=10, depth=2, location=(0,0,1))
bpy.context.active_object.name = "Pedestal_BaseRing1"
bpy.ops.mesh.primitive_cylinder_add(radius=8, depth=1, location=(0,0,2))
bpy.context.active_object.name = "Pedestal_BaseRing2"
bpy.ops.mesh.primitive_cube_add(size=2, location=(0,0,4.5))
ped = bpy.context.active_object
ped.name = "Pedestal_Main"
ped.scale = (5,5,2.5)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0,0,6.5))
top = bpy.context.active_object
top.name = "Pedestal_TopGlow"
top.scale = (4,4,0.5)
for i in range(PILLARS):
    angle = (i / PILLARS) * 2 * math.pi
    x = math.cos(angle) * PILLAR_RADIUS
    y = math.sin(angle) * PILLAR_RADIUS
    bpy.ops.mesh.primitive_cylinder_add(radius=2, depth=25, location=(x,y,12.5))
    bpy.context.active_object.name = f"Pillar_{i+1}"
for i in range(16):
    angle = (i / 16) * 2 * math.pi
    x = math.cos(angle) * (RADIUS+2)
    y = math.sin(angle) * (RADIUS+2)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(x,y,10))
    wall = bpy.context.active_object
    wall.name = f"LabyrinthWall_{i+1}"
    wall.scale = (7.5,1,10)
    wall.rotation_euler = (0,0,angle)
pad_locs = [(30,0), (-30,0), (0,30), (0,-30), (21,21), (-21,21), (-21,-21), (21,-21)]
for idx, (x,y) in enumerate(pad_locs):
    bpy.ops.mesh.primitive_cylinder_add(radius=4, depth=0.5, location=(x,y,0.25))
    bpy.context.active_object.name = f"TeleportPad_{idx+1}"
trophy_path = os.path.expanduser("~/Documents/roblox-scripting-demos/assets/trophy/Labyrinth_Trophy_BIG.obj")
if os.path.exists(trophy_path):
    bpy.ops.wm.obj_import(filepath=trophy_path)
    trophy = bpy.context.selected_objects[0]
    trophy.name = "Labyrinth_Trophy_BIG"
    trophy.location = (0,0,8.5)
    trophy.scale = (6.5,10.7,6.5)
print("=== LABYRINTH LOBBY BUILT ===")

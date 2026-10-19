return [==[
# Project memory
## Overview
Obby/parkour game with 5-floor runs, lobby, rebirth prestige system.
## Where things live
- Server logic: ServerScriptService.Main; remotes in ReplicatedStorage.Remotes (Rebirth, RebirthLobby).
- Client: StarterPlayer.StarterPlayerScripts.Main / Parkour / UI.
- Lobby props under Workspace.Lobby. CURRENT rebirth portal = Workspace.Lobby.RebirthPortalBlender: a SINGLE real uploaded MeshPart 'body_geom' (13 x 11.8 x 3.4, upright at identity rotation, bottom on floor Y=50.303, center Y~56.2, at -16,5090) made with the generate_mesh tool. Model also holds PortalFX_Center (PointLight PortalGlow + ParticleEmitter PortalSparkles) and Script PortalAnimator; body_geom has ProximityPrompt "RebirthPrompt" and CanCollide=true.
- HISTORY: procedural RebirthPortalOrnate (~173 parts) was built then deleted; a Blender-authored version was also attempted and removed.
- DELETED over time: RebirthPortal (original), RebirthPortalNew (procedural), RebirthPortalMesh (AI mesh), station parts RebirthStation/Ring1/Ring2/StationBevel/StationBase, RebirthRingSpinner script.
- Billboard/sign text: RebirthBillboard.BillboardGui (Title/Subtitle/InfoText) + RebirthStationSign.SurfaceGui (Title/InfoText). Live-updated per player by StarterPlayerScripts.PortalTextUpdater (reads GetProgression, RunState, RunEvent REBIRTH).
- RebirthPortalOrnate structure: OuterRing + InnerRing (segment rings, Metal gold), EnergyDisc (neon cylinder, holds the ProximityPrompt "RebirthPrompt"), 12 RuneStud balls, 2 Pillars + 2 Finials, stepped pedestal (PedestalLower/Mid/Top). Model must be parented to Lobby or it is discarded.
- PortalSwirl model: SwirlPivot + SwirlBlade1-3 (neon pinwheel in front of disc), spun by Script PortalSwirl.PortalSwirlSpinner. GOTCHA: destroying the swirl model also destroys that Script - rebuild both together.
- Portal FX: PortalFX_Center (invisible part) holds PointLight 'PortalGlow' + ParticleEmitter 'PortalSparkles'; Script PortalAnimator pulses brightness/range/rate with slow violet hue drift.
- RebirthStationSign at Y~65.4 and RebirthBillboard at Y~67.4 sit above the portal; lobby ceiling Y~101.
- IMPORTANT: LobbyBuilder line ~771 used to call buildStationPro for RebirthStation at runtime, recreating a marble pedestal + neon sphere + PointLight inside the portal (made it look like a white block). That line is now replaced with a comment - do NOT re-add it.
## Conventions
- Client handles any ProximityPrompt named "RebirthPrompt" via ProximityPromptService.PromptTriggered (global, no per-prompt wiring).
- Server Main trusts RebirthLobby remote, no position validation.
## Key systems
Rebirth: prompt -> ui.showRebirthConfirm -> RebirthLobbyRE:FireServer(); rebirths grant permanent speed bonus (Config.rebirthSpeedMult, applied via parkourHandle.setRebirthMult).
## MISTAKES LOG (check before acting - do not repeat)
1. Default collision fidelity on a collidable frame = INVISIBLE WALL filling the arch. Use PreciseConvexDecomposition on the collidable frame only; Box on everything non-colliding.
2. Missing vortex plane - the swirl had blades but no counter-rotating texture. Both are required by the art brief.
3. Blender auto-export hook (addon blender_addon_labyrinth_bridge, @persistent save_post -> labyrinth.export_trophy) overwrote Labyrinth_Trophy_BIG.obj 3x. Fixed via prefs.auto_export=False + save_userpref() + removing the runtime handler. Do NOT re-enable.
4. 6 non-colliding MeshParts were still storing collision geometry (Default fidelity) despite CanCollide=false. Always Box non-colliding meshes.
5. AssetId confusion: 140476554674370 is V9. V10.1 is 78508116651933. Check before shipping.
6. EXCESS DEPTH is not always the pylon assemblies - measure per-part Z ranges first. On V10 the STONE band was the deepest element; the fix was a Z-only scale (0.8521) about the model centre, not moving pylons.
7. PROMPT PRIORITY TRAP: two ProximityPrompts on one model compete. Roblox triggers the NEAREST enabled prompt. A wide-radius prompt (RebirthPrompt, 12 studs) beats a narrow one (5 studs) because its anchor is usually closer. Fix = give the second prompt its own anchor placed NEARER the approach path (V10: PortalEnterAnchor at Z=5086.77, 1.2 studs in front of the stone face) with a 6-stud radius. Verified: enter prompt 1.57 studs vs rebirth 5.48.
8. Server cannot call RemoteEvent:FireServer() - that is client-only and errors. In server fallbacks use FireClient/FireAllClients instead.
9. NEVER trust an audio asset ID given in a prompt without verifying it. ID 12222058 was passed in as a 'portal hum' but is actually 'Kid saying Ouch.wav' (type 3 Audio, public domain - so every automated check passes). Always call MarketplaceService:GetProductInfo(id) and READ THE NAME before wiring a Sound. Found the real loop via search_asset(query='portal ambient hum loop', assetType='Audio').
10. Procedural texture masks need calibration against the actual output, not just the code. First moss pass produced 0.2% coverage (threshold too tight), second produced 83% (looked like a green rock). Landed on a mean RGB of 0.132/0.151/0.150 as the acceptance test - always print the measured statistics after generating, do not assume the formula worked.

## Decisions & gotchas
- PBR PIPELINE (verified, THE fix for flat-looking meshes): SurfaceAppearance REQUIRES UVs on the mesh. Procedural/primitive Blender geometry has NO UVs by default -> always run a UV unwrap before export. Use bpy.ops.uv.cube_project(cube_size=1.0) for architectural parts (Smart UV Project produces smeared/uneven texel density on extruded arches). Then upload albedo/normal/roughness PNGs with upload_image and set sa.ColorMap / sa.NormalMap / sa.RoughnessMap. GOTCHAS: (1) SurfaceAppearance has NO TileSize property in this build - do not set it. (2) The part's Color MULTIPLIES the albedo, so keep Color white-ish; a warm Color or the lobby's amber lighting will tint grey stone brown - use a cool tint like (198,214,235) to counteract. (3) Albedo generated at mean 0.44 washed out to cream; mean ~0.18 reads as proper dark granite. (4) Set part.Material=SmoothPlastic when using SurfaceAppearance.
- WORKING IMAGE PIPELINE (verified): upload_image only accepts http/https URLs, NOT local file paths. Solution that works: serve files from a local HTTP server via Blender python (ThreadingHTTPServer on 127.0.0.1:8765 serving C:\Users\Etern\Desktop\portal_serve), then call upload_image with http://127.0.0.1:8765/name.png. Returns real rbxassetid:// values. Blender python has numpy but NO PIL - procedural textures are written with a hand-rolled PNG encoder (zlib + struct, RGBA8).
- Portal VFX textures (all procedurally generated, original): vfx_sparkle 132615638177647, vfx_smoke 122797529777837, vfx_streak 117955068921816, vfx_ring 106109636037032, vfx_swirl 132243950328744, vfx_dot 84201278885109. Wired onto the portal: PortalFX.PortalSparkles (star), PortalFX.PortalSmoke (aura), PortalFX.PortalRingPulse (expanding ring), and a BladeStreak emitter on each of the 7 swirl blades.
- WORKING MESH PIPELINE (verified): Open Cloud Assets API. POST https://apis.roblox.com/assets/v1/assets, multipart/form-data with x-api-key header, fields "request" (JSON) + "fileContent". Use assetType **Model** with the .fbx - assetType **Mesh** is REJECTED ("Creating Mesh from a application/octet-stream file is not supported yet"). request JSON = {assetType, displayName, description, creationContext:{creator:{userId}}}. Then poll GET /assets/v1/operations/{operationId} until done:true -> response.assetId. API key must have the assets asset:write permission; key file lives at C:\Users\Etern\Desktop\roblox_api_key.txt (960 chars = 48-char key + JWT; always read with utf-8-sig). CreateAssetAsync (the in-engine upload API) is feature-flagged off in this Studio build, even from a plugin.
- GOTCHA importing an uploaded FBX model: the parts arrive at ~100x scale (Blender cm) and with a BAKED rotation. Do NOT apply CFrame.Angles to stand it up - the correct orientation is IDENTITY. To reposition without flattening it, rebuild each part's CFrame from Position only (CFrame.new(pos)), never from its existing CFrame. Model:ScaleTo works for scale. MeshParts also misreport Size/bounds - trust screen_capture over GetBoundingBox.
- CURRENT rebirth portal = Workspace.Lobby.PortalGateV8 (asset 127399982876366). 7 parts: PortalStone (PBR granite), PortalMetal (PBR steel, 21 RUNE RECESSES CARVED via boolean), PortalRunes (neon inserts sitting in the recesses), PortalBrackets (5 iron housing assemblies), PortalRivets (copper bolt heads), PortalOrbs (5 cyan sphere orbs), PortalEnergyDisc (Neon violet core, holds RebirthPrompt + PortalSwirl). 10.36W x 13.5H x 4.3D. PortalFX holds PointLight 'CoolFill' (120,200,255, range 12, Shadows ON - this neutralises the lobby's amber tint so granite reads grey) + PointLight 'PortalGlow' + PortalSparkles.
- PREVIOUS portal = Workspace.Lobby.PortalGateV7 (asset 86128047080882), built to the concept sheet: ARCH shape (not circle), weathered stone outer band + black metal inner trim, 5 anchor pylons with cyan orbs, cyan runes on the metal face, pink/purple vortex core, 11.8W x 13.5H x 5.48D (real depth). Parts: PortalStone (SurfaceAppearance granite), PortalMetal (SurfaceAppearance steel), PortalRunes (Neon cyan), PortalEnergyDisc (Neon violet, holds RebirthPrompt + PortalFX + PortalSwirl). PBR textures: stone2_albedo 82958854475101 / stone2_normal 108044660987340 / stone2_rough 89729363546186; metal_albedo 124061622949188 / metal_normal 89499338418733.
- Older portal (v4) = Workspace.Lobby.RebirthPortalV4 (uploaded Model asset 140536045298135). 3 parts: PortalFrame (8.56 x 9.64, 1.9 deep), PortalRunes, PortalEnergyDisc (5 diameter, 0.45 deep). Real 5-axis volume. IDENTITY CFrame is correct on import (the 47-degree tilt the FBX carries is wrong - always override with CFrame.new(CX,0,CZ)). Frame bronze Metal (168,122,44) refl 0.2; runes Neon cyan inset at frame Z; disc Neon purple. PortalFX holds glow+sparkles+smoke+ring; PortalSwirl holds 7 blades + SwirlCore + PortalSwirlSpinner. Previous v1 kept in ServerStorage as RebirthPortalBlenderModel (fallback).
- OLDER portal (v1) = Workspace.Lobby.RebirthPortalBlenderModel (uploaded Model asset 102382647223587) with parts PortalFrame / PortalRunes / PortalEnergyDisc, seat on floor Y=50.303 at (-16, 5090), identity rotation, ~13 studs tall. Frame set Metal gold, Runes Neon cyan, Disc Neon purple @0.15 transparency. PortalEnergyDisc holds the RebirthPrompt; child Part 'PortalFX' holds PointLight PortalGlow + ParticleEmitter PortalSparkles. Child Model 'PortalSwirl' (SwirlPivot + SwirlBlade1-7 + SwirlCore) sits in front of the disc at (-16, 56.575, 5089.55) and is spun by Script PortalSwirl.PortalSwirlSpinner (~0.9 rad/s). NOTE: destroying the PortalSwirl model also destroys that Script - rebuild both together. Verified rendering + animating correctly in Play mode.
- PORTAL COLLISION RULE: PortalFrame/PortalRunes/PortalEnergyDisc must all have CanCollide=false and CanTouch=false (a MeshPart frame with CanCollide + Default fidelity fills the ring hole and blocks the player). All three use DoubleSided=true and PreciseConvexDecomposition. Swirl blades/core are CanCollide/CanTouch/CanQuery=false. The ProximityPrompt on PortalEnergyDisc still works because prompts don't need collision.
- Swirl look: blades recoloured violet (200,140,255) at ~0.6 transparency and scaled 0.7x so they read as energy wisps, not white bars. A 'SwirlTexture' part sits inside PortalSwirl at disc centre -0.7 Z, size ~0.88*disc width square, part Transparency=1 with two Texture decals (vfx_swirl) at 0.35 transparency, counter-rotated in PortalSwirlSpinner. GOTCHA: a square part with Neon material plus a decal renders as a glowing white square - the part MUST be Transparency=1 so only the decal shows.
- CRITICAL: EditableMesh -> AssetService:CreateMeshPartAsync(Content.fromObject(em)) makes a MeshPart with an EMPTY MeshId. It renders fine in Edit but in Play it becomes a placeholder block (no asset behind it). It is NOT a substitute for importing a mesh. CreateAssetAsync is "not available yet", em has no Save/Publish. Only generate_mesh / generate_procedural_model / Studio's 3D Importer produce real persistent meshes.
- execute_luau can use HttpService to fetch local data (Blender-served JSON on 127.0.0.1:8765 worked) - but that only solves DATA transfer, not mesh persistence.
- GetBoundingBox is Model-only, not on MeshPart. EditableMesh-created MeshParts also misreport Size/axes; compute world bounds manually from CFrame and Size.
- Blender Z-up -> Roblox Y-up conversion: (x, z, y). generate_mesh output is authored upright already, so keep identity rotation.
- Blender MCP has no top-level `return` in execute_blender_code (SyntaxError); use print.
- Blender 5.2: Material has NO .emission_color/.metallic attributes - must use use_nodes=True and set Principled BSDF inputs ("Base Color", "Metallic", "Roughness", "Emission Color", "Emission Strength").
- Blender MCP generate_3d is DISABLED (needs Hunyuan3D/Hyper3D key) - build models procedurally with bpy instead.
- Blender 'look' modes: viewport, camera, angles, frames (NOT 'render'). angles gives a 4-view tile.
- Blender 5.2.2 BOOLEAN solver enum is only ('FLOAT','EXACT','MANIFOLD') - there is NO 'FAST'. Use MANIFOLD for carving (EXACT collapsed a 260-vert band to 6 verts). Apply cutters ONE AT A TIME (separate modifier per cutter, bake via evaluated_depsgraph_get + new_from_object) rather than joining many disjoint cutters into one boolean object.
- FBX import MIRRORS the Z axis: detail layers authored in front of a band end up buried INSIDE it after import. Fix by measuring the host part's world front face and pushing each detail part forward with (front - proud_offset).
- Roblox can't import local FBX/OBJ via MCP - user must import meshes through Studio UI (no Roblox command can read a local file).
- Blender project files on disk: Desktop\\rebirth_portal.blend (full project), Desktop\\rebirth_portal_blender.fbx (PortalFrame + PortalEnergyDisc + PortalRunes), Desktop\\rebirth_portal.obj.
- GOTCHA: Blender on this machine has an auto-export/push hook - saving/exporting fires an extra export to Documents\\roblox-scripting-demos\\assets\\trophy\\Labyrinth_Trophy_BIG.obj and logs 'will auto-push'. That watch pipeline is LOCAL ONLY (see assets\\sync_manifest.json) and does NOT deliver anything into Roblox Studio. It already overwrote the old trophy OBJ with portal geometry (user said the trophy was old, so that is fine).
- Sketchfab license check: avoid CC BY-NC-ND for game use.
## Lobby boards / signs (2026-10-17)
- StartSign was floating 16 studs wide directly in front of the Rebirth portal, blocking the sightline from the pad. Moved to (34, 58.5, 5005), east side.
- Rebirth signs were left at z=5090 when the portal moved to z=4970 - 120 studs away from it. RebirthStationSign -> (0,70,4973), RebirthBillboard -> (0,73,4973).
- GOTCHA: RebirthStationSign only had a FRONT-facing SurfaceGui, so approaching from +Z showed a blank back. Clone the Front SurfaceGui and set Face = Back.
- GOTCHA: placing a sign at the same z as the portal buries it inside the arch. Push signs forward (+Z toward the player) and above the crown top.
- UpdateBoard -> (-40,56,5085), InfoBoard -> (0,58,5105).

## User preferences
- **"PERM"** = shorthand for "save this permanently". When the user says PERM, write the learnings to this file immediately, no confirmation.

## AUTO-PERM PROTOCOL (self-enforcing - read this before editing anything)
**The user should NEVER have to repeat a fact, a fix, or a pipeline to you.** If you had to work it out, it goes in memory the same turn you work it out - not when asked.

- WRITE IMMEDIATELY, DO NOT ASK. New verified fact, working recipe, gotcha, or user preference -> multi_edit this file before ending the turn. Never say "want me to save that?" - just save it and mention it in one line.
- VERIFIED ONLY. Never persist a guess as fact (see the MISTAKES LOG rule). Tag anything unconfirmed as `(UNVERIFIED)`. If a recorded fix does not clear the symptom, DELETE that entry instead of re-applying it.
- ONE SOURCE OF TRUTH PER FACT. If a new finding contradicts an old entry, replace it. Never leave both. Mark superseded sections `## (superseded)`.
- PIPELINES LIVE IN Desktop\3D_Tools\PIPELINES.md. Any recipe that took more than one attempt to get right (upload MIME, rbxmx schema, normal-map baking, mesh upload, image server) is a PIPELINE and must be registered there with its exact working commands. Run `python Desktop\MetaAI_Logs\perm_sync.py add` to append one.
- DISK MIRROR. After any meaningful memory edit, run the dump step so a lost place file cannot lose the memory. Command sequence is in PIPELINES.md under 'memory mirror'.
- THE TEST: if the user has to explain the same thing twice, this protocol failed. Treat a repeat question as a BUG report about memory, not as a new question.
- Prefers free/CC assets only.
- RED = DIAGNOSE, DO NOT PATCH: whenever something comes up red (a bug, a failed bake, a flat texture, a broken render), ALWAYS seek to understand WHY and state the root cause - never just paper over the symptom or move on silently. Investigate the actual mechanism, confirm it, then fix. (Stated 2026-10-18.)
- HAS ADD. Keep replies SHORT. Never dump long walls of text.
- Wants COLOUR CODING and HIGHLIGHTED KEYWORDS in every reply. Use emoji as colour tags: 🟢 good/done, 🔴 problem/bug, 🟡 caution/partial, 🔵 info/next step. Bold the key words. Break things into small scannable chunks, not paragraphs.
## LOCKED: PORTAL V10.3 FINAL (do not overwrite) - TRUE PRODUCTION FINAL
- Lobby: Workspace.Lobby.PortalGateV10_FINAL, assetId 78508116651933. Attributes: version=v10.3_final, locked=true, fadeFallbackTimer=true, fadePrimaryPath='RunEvent.LOBBY_COUNTDOWN', fadeFallbackDelay=3.5, humHysteresis='15/18', humSoundId=7028127341, depthRatio='3.33:1', tris=6250, verifiedInPlay=true.
- PIPELINE MEMORY WRITTEN TO DISK: Desktop\\portal_pipeline.json (2951 bytes) + Desktop\\Portal_V10_3_FINAL.blend (1,074,587 bytes with 15 packed files and an embedded text block 'PIPELINE_NOTES'). Load these instead of rebuilding.
- FADE: primary = RunEvent LOBBY_COUNTDOWN when seconds<=1 (0.55s fade). Fallback = 3.5s Task.delay armed on Prompt.Triggered, guarded by fadeGeneration (stale timers bail) + fired flag (no double-fire) + didFallback marker. Both paths call the single doFade(reason,duration) helper which prints '[PortalEntry] fade fired via <reason>'. VERIFIED: console printed 'fade fired via LOBBY_COUNTDOWN'; timeline showed transparency 1.00 until 3.0s, 0.67 at 3.4s, 0.00 by 3.8s, teleport to (790,-210) at 4.4s while faded, clear by 6.2s.
- MCP REALITY CHECK: only 'roblox' and 'blender' servers are connected. There is NO filesystem_mcp, memory_mcp, http_mcp, image_gen, image_search or web_search in this environment. Filesystem writes go through Blender's Python; memory goes in this ModuleScript. Do not promise MCP features that are not connected - run list_mcp_servers first.
## (superseded) LOCKED: PORTAL V10.1 FINAL
- Lobby instance: Workspace.Lobby.PortalGateV10_FINAL (Model), assetId 78508116651933. Attributes: version=v10.1_final, locked=true, depthRatio=3.33:1, depthStuds=4.04, heightStuds=13.5, tris=6250, sculpted=true, verifiedInPlay=true.
- Dimensions: 10.19W x 13.5H x 4.04D = 3.33:1 height:depth, matching the concept sheet's 3.0M:0.9M exactly.
- SCULPTED BUILD: stone was subdivided to 21,634 verts and displaced with 3-octave noise (AMP 0.028/0.013/0.005 at freq 3.2/11/34), then decimated to 1,998 tris. Metal sculpted similarly then carved with 21 MANIFOLD boolean rune channels. 46 cylinder bolts as real rivet geometry. 5 pylon assemblies each with backplate + cylindrical orb housing + copper rim + orb + cable conduit + 4 bracket bolts.
- TRI BUDGET: stone 1998, metal 1200, brackets 500, fittings 800, orbs 900, rivets 600, runes 252 = 6250 total (budget 7000).
- BAKED MAPS (from high-poly sculpt, use_cage, cage_extrusion 0.25, max_ray_distance 0.40, low scaled 1.012 outward):
  stone_normal rbxassetid://118973822714830 (54.2% detail coverage) / stone_ao rbxassetid://100384605516412
  metal_normal rbxassetid://78728004826825 (19.2% detail) / metal_ao rbxassetid://124438496807848
- DEPTH CORRECTION GOTCHA: the excess depth was NOT the pylons (they sit inside the stone's Z range) - the stone band itself was the deepest element. Fixed by scaling ONLY Z by 0.8521 about the model centre, leaving X/Y untouched so the silhouette is preserved. Do not move pylons to fix depth; measure first.
- Colliders: PortalStone + PortalMetal, both PreciseConvexDecomposition. All detail parts + core non-colliding.
- BACKUP: PortalGateV9_FINAL still parked in ServerStorage (do not overwrite).
- PORTAL MECHANIC (v10.1, shipped + verified in Play):
  ServerScriptService.PortalEntryServer + StarterPlayerScripts.PortalEntryClient + RemoteEvent ReplicatedStorage.Remotes.PortalEnter.
  Prompt 'EnterLabyrinthPrompt' (0.8s hold, 6 stud radius) on Model child Part 'PortalEnterAnchor' (invisible, at Z=5086.77).
  Flow: prompt -> PortalEnter:FireServer -> server validates proximity (<=12 studs) + 2s per-player cooldown -> FloorManager.requestPlay(player) -> pad countdown -> startRun -> maze. DO NOT teleport directly to the maze; that bypasses run state.
  VERIFIED END-TO-END: character went from Z=5086 in the lobby to X=790 Z=-210 inside Worldsplague_Maze.
  Client FX: CoolFill brightness flash, orb colour pulse, 3-beat rune flash. PortalEnter:FireClient(player,'enter'|'retry').
  FADE TIMING (v10.2, verified by sampling PlayerGui.PortalFade.BackgroundTransparency at 0.2s intervals): the purple fade is NOT triggered by the prompt. It is driven by RunEvent's LOBBY_COUNTDOWN event - when evt.seconds <= 1 the client fades in over 0.55s, and LOBBY_COUNTDOWN_END schedules fadeOut 1.2s later. Measured result: pad at (-1,4997) with transparency 1.00 until 3.0s, fade to 0.00 by 3.6s, teleport to (790,-210) at ~4.6s WHILE fully faded, fade lifts by 6.0s. Do not move the fade back into the PromptTriggered handler.
  HUM GATING: Sound PortalHum lives on PortalStone (not PortalFX), Volume 0.15, Looped, InverseTapered, RollOffMin 5 / Max 25, PlaybackSpeed 0.85, SoundId rbxassetid://7028127341. PortalEntryClient polls every 0.3s and plays within 15 studs / stops beyond 18 (hysteresis band so it does not stutter). Verified playing at 5.7 studs and stopped at 5361 studs.
  PORTAL HUM: Sound 'PortalHum' on PortalFX, SoundId rbxassetid://7028127341 ('Noise Ambience' by imminium, free, 30s seamless loop), Volume 0.35, Looped, RollOffMode InverseTapered, RollOffMin 6 / Max 45, PlaybackSpeed 0.85. Started client-side in PortalEntryClient; swells to 2.4x then tweens back over 0.7s on 'enter'. Verified IsLoaded + IsPlaying in Play mode.
  STONE ALBEDO VARIATION 2: rbxassetid://105120361275959 (1024x1024, cool granite mean RGB 0.132/0.151/0.150, moss lining the cracks, 54.4% crack coverage). Replaced the v1 albedo 82958854475101 on PortalStone's SurfaceAppearance.
## (superseded) PORTAL V9.1 FINAL
- V9.1 verification pass COMPLETE. Attributes on Workspace.Lobby.PortalGateV9_FINAL: version=v9.1_final, collisionFixed=true, counterRotateWired=true, characterPassVerified=true, hookDisabled=true, locked=true.
- CHARACTER PASS PROVEN: walked from Z=5084 (in front) to Z=5096 (behind) through the arch with character_navigation; final pos Z=5095.2, X stayed centred at -16, i.e. 3.04 studs PAST the stone back face (5092.15). Colliders are PortalStone + PortalMetal both PreciseConvexDecomposition, so the arch opening is genuinely walkable.
- BLENDER AUTO-EXPORT HOOK KILLED: the culprit was the addon `blender_addon_labyrinth_bridge`, its @persistent save_post handler `on_save_post` calling `labyrinth.export_trophy()`. Disabled via prefs.auto_export = False + bpy.ops.wm.save_userpref() so it persists across restarts, AND removed the runtime handler from bpy.app.handlers.save_post. Verified by saving the blend and confirming Labyrinth_Trophy_BIG.obj mtime/size unchanged (512546 bytes). Do NOT re-enable that addon's auto_export.
- V9.1 adds a counter-rotating vortex plane: PortalSwirl.SwirlTexture, size 5.52 x 10.07 (matched to the disc's real 6.42W x 11.71H aspect), part Transparency=1 with two Texture decals (vfx_swirl 132243950328744) at 0.25, spun at -1.4 rad/s against the blades' +0.8 rad/s.
## (superseded) PORTAL V9 FINAL
- Lobby instance: Workspace.Lobby.PortalGateV9_FINAL (Model), assetId 140476554674370. Attributes: version=v9_final, locked=true, verifiedInPlay=true, depthStuds=4.3, heightStuds=13.5. 30 descendants.
- Dimensions: 11.07W x 13.5H x 4.3D. Bottom on floor Y=50.303, centred at (-16, 5090). Identity rotation (FBX carries a bogus baked tilt; always override with CFrame.new(CX,0,CZ)).
- Backups on disk: Desktop\\Portal_V9_Final.blend (234 KB) + Desktop\\Portal_V9_Final.fbx (213 KB, 8 objects, 3422 verts).
- PBR IDs (verified live):
  STONE  albedo rbxassetid://82958854475101 / normal rbxassetid://108044660987340 / roughness rbxassetid://89729363546186 / tint (198,214,235)
  METAL  albedo rbxassetid://124061622949188 / normal rbxassetid://96116556147140 (BAKED rune relief) / tint (210,215,230)
  BRACKETS albedo rbxassetid://124061622949188 / normal rbxassetid://89499338418733
- Lighting: PortalFX.CoolFill PointLight = RGB 120,200,255, Range 12, Shadows ON (neutralises the amber lobby tint). PortalFX.PortalGlow = 185,120,255 range 28. PortalSparkles emitter on PortalFX.
- Structure: PortalStone (980v, cracked protrusions + 0.03 bevel), PortalMetal (600v, 21 carved rune recesses), PortalRunes (168v neon inserts), PortalBrackets (5 assemblies), PortalRivets (600v copper), PortalOrbs (5 cyan), PortalMoss (294v, 7 clumps), PortalEnergyDisc (60v core) + PortalSwirl (9 blades + SwirlCore, spun by PortalSwirlSpinner).
- STATUS: FINAL at v9.1. No further geometry changes.
## GOLD MASTER LOCKED: V10.4.1 (2026-10-17)
- V10.4.1 assetId **123021752328888** REPLACES 110650213478858 (V10.4) which replaced 78508116651933 (V10.3).
- Git: commit **e70f14d** on main, supersedes 174ed6b and e3e7c7e.
- ROOT CAUSE of the arch bug: the LIVE STUDIO INSTANCE was rebuilt with Instance.new using the wrong Roblox Cylinder axis order. The Blender source was correct all along (PortalCoreArch thin on Blender Y = thin on Roblox Z). Always measure the source before assuming the asset is wrong.
- ROBLOX CYLINDER AXIS RULE: local X is the axis between the two flat faces. Size (thickness, diameter, diameter) plus a 90 deg Y rotation = a disc facing Z. Wrong order gives a thick band.
- VERIFIED inside the inserted asset: PortalCoreArch 0.61 world-Z on 1.26 diameter = thin disc, not a band.
- Entry re-verified: Z=5086 -> (790,-210), transparency 1.00 until 3.0s, 0.82 at 3.4s, 0.00 by 3.8s, teleport ~5.0s while faded.
- NOT DONE (manual step): docs/Portal_V10_4_1_FULL.rbxm. Saving a full model with Beams/Attachments/Prompts/Scripts/Sounds requires Studio's File > Save to File dialog; no MCP command can do it. The location note in the repo documents this.

## (superseded) GOLD MASTER LOCKED: V10.4
- V10.4 assetId **110650213478858** REPLACES V10.3's 78508116651933. Reason: V10.3 shipped a MeshPart (PortalEnergyDisc) created via Instance.new with an EMPTY MeshId, which renders as the magenta checkerboard placeholder. Do NOT re-insert 78508116651933 - it brings the bug back.
- Git: commit **174ed6b** on main in C:\Users\Etern\Documents\roblox-scripting-demos (supersedes e3e7c7e). Files: docs/portal_pipeline.json + docs/Portal_V10_4_FINAL.blend.location.txt.
- Blender source: Desktop\\Portal_V10_4_FINAL.blend (1,077,309 bytes) and Desktop\\portal_v10_4.fbx (273,708 bytes).
- Geometry: 9 meshes, 6,450 tris. New PortalCoreLower (block) + PortalCoreArch (cylinder) replace the broken MeshPart and follow the stone arch silhouette.
- Live Studio instance is STILL named PortalGateV10_FINAL and now holds the V10.4 geometry plus the beam vortex.
- VERIFIED IN PLAY: entry Z=5086 -> (790,-211); fade transparency 1.00 until 3.0s, 0.63 at 3.4s, 0.00 by 3.8s, teleport at ~4.4s while faded; hum 7028127341 with 15/18 hysteresis.
- CRITICAL UPLOAD LIMITATION (learned): an uploaded Model asset contains FBX GEOMETRY ONLY. Beams, Attachments, ProximityPrompts, Sounds, PointLights, SurfaceAppearances, Textures and Scripts do NOT survive upload - they must be re-applied in Studio after insert_asset. Currently the live model has 4 Beams, 8 Attachments, 2 ProximityPrompts, 1 Script, 2 PointLights, 1 ParticleEmitter, 1 Sound, 3 SurfaceAppearances - none of which are in asset 110650213478858.

## (superseded) GOLD MASTER LOCKED: V10.3
- V10.3_FINAL is the ship. Workspace.Lobby.PortalGateV10_FINAL, roblox assetId 78508116651933.
- LOCAL GIT COMMITTED: C:\Users\Etern\Documents\roblox-scripting-demos, commit e3e7c7e on branch main. Files: docs/portal_pipeline.json (4470 bytes) + docs/Portal_V10_3_FINAL.blend.location.txt (562 bytes, records the ~1MB blend path/size/packing instead of committing the binary). 103 insertions, 2 files.
- Deliberately NOT staged: assets/sync_manifest.json and assets/trophy/Labyrinth_Trophy_BIG.{obj,mtl} - those were dirtied by the old auto-export hook before it was disabled. Left them alone rather than bundling unrelated changes into the gold-master commit.
- NO GITHUB PUSH YET. Only roblox + blender MCP are connected; a github MCP server must be registered in ZeroScript settings and authenticated by the user. I cannot register it or hold their token.
- Spec unchanged: 10.19W x 13.5H x 4.04D (3.33:1), 6250 tris, Z=5086 -> (790,-210), fade 3.8s + 3.5s fallback, hum 7028127341, prompt anchor Z=5086.77.

## Cleanup done (2026-10-17)
- DELETED from Workspace: the stray empty MeshPart at (0,62,5000) - my leftover EditableMesh test quad (MeshId == "").
- DELETED from ServerStorage: ZZ_PLUGIN_REPORT (my plugin test StringValue), plus obsolete portal backups RebirthPortalBlenderModel / RebirthPortalV4 / PortalGateV5 / V6 / V7 / V8, plus the 8 parked SkillsStation*/TrailsStation* parts.
- ServerStorage now holds only: PortalGateV9_FINAL (the v9.1 keeper), PortalV10_Handoff, plus the user's own Secrets / ZeroScript / TempId.

## Lobby portals (Skills / Trails / Rebirth)
- Skills + Trails were REBUILT as clones of the Rebirth portal's 7 MeshParts (PortalStone/Metal/Brackets/Fittings/Rivets/Orbs/Runes) instead of hand-built primitives. Cloning a MeshPart copies its MeshId, so all three share the same geometry - do that instead of rebuilding shapes.
- Each clone is offset by (target - source) position. PortalRunes/PortalOrbs are tinted Neon accent per portal; PortalFittings/PortalRivets get copper.
- GOTCHA: the first tint attempt used a near-white glow (150,100,255) at 0.5 transparency, which washed the whole core out. Rebirth's working glow is much darker (96,34,176). Landed on core 38,16,88 + glow 110,70,220 for Skills and 16,62,70 / 40,170,180 for Trails.
- GOTCHA: GlowLower (rectangle) and GlowArch (cylinder) OVERLAP, doubling brightness and leaving a visible horizontal seam across the portal. Fix was to delete both glow sheets and make the core itself Neon at 0.28 transparency.
- Verified in Play: SkillsPrompt opens SkillsPanel (300x300) and TrailsPrompt opens TrailsPanel (336x374).
- Three matching arch portals now exist in Workspace.Lobby, all built from the same recipe:
  PortalGateV10_FINAL at (-16, 5090) = REBIRTH, purple/violet core, prompts EnterLabyrinthPrompt(6) + RebirthPrompt(12)
  SkillsPortal at (-16, 5034) = SKILLS, violet core Color3(38,16,88) with glow (150,100,255), prompt SkillsPrompt(10)
  TrailsPortal at (16, 5034) = TRAILS, teal core Color3(16,62,70) with glow (80,255,240), prompt TrailsPrompt(10)
- Each portal: CoreLower (block) + CoreArch (cylinder, Size=(thickness, diameter, diameter) + 90 deg Y rotation), GlowLower/GlowArch neon sheets at 0.5 transparency, Swirl model with 4 Beams + 8 Attachments + SwirlPivot + SwirlCore, a SwirlSpinner Script, and a PortalFX part holding a PointLight.
- ARCH FRAME RECIPE: two Pillar parts (not a solid block - a solid block buries the core and renders as a flat wall), plus ~11 Crown segments laid along the arc with Size=(thick, pillarW, chord) oriented by CFrame.lookAt(mid, mid+tangent). Getting the crown axis wrong leaves gaps that the core glow bleeds through.
- Old station parts (SkillsStation*, TrailsStation*) were parked in ServerStorage, not deleted.
- GOTCHA: the yellow blobs seen over the Rebirth core were PortalBrackets/PortalFittings/PortalOrbs poking through a 0.30-thick core. Fixed by thickening the core to 1.60 so it spans 5089.20-5090.80 and covers them.
- FIXED: Skills/Trails panels are now mutually exclusive. Added ui.closeTrailsPanel() and ui.closeSkillsPanel() to StarterPlayerScripts.UI (both panels are Frames parented to `gui`, destroyed by name). openSkillsPanel calls closeTrailsPanel first and vice versa, so both the GUI buttons and the ProximityPrompts get the behaviour. Verified in Play: opening Trails removes SkillsPanel entirely (skillsPanelExists=false).

## Lobby layout Option B + Skills finial (2026-10-17)
- LAYOUT CHANGED TO OPTION B (linear corridor): all three portals moved to z=4970, evenly spaced in X - SkillsPortal (-55,4970), PortalGateV10_FINAL (0,4970), TrailsPortal (55,4970). Walk order is now carpet z=5030 -> pad z=5000 -> portals z=4970. FIRST ATTEMPT FAILED: placing them at z=5010 put the rebirth portal between the carpet and the pad, blocking the walk. Portals must sit BEYOND the pad.
- Moving a portal = offset every BasePart in the model by the same (dx,dz). The ProximityPrompts, Beams, Attachments and Scripts ride along as children - verified all 4 prompts survived (SkillsPrompt, TrailsPrompt, RebirthPrompt, EnterLabyrinthPrompt).
- SKILLS FINIAL: Workspace.Lobby.SkillsFinial, assetId 116676890468076, a Blender-built crystal cluster (1 tall spire + 6 smaller shards on a stone ring base, 550 tris, UV'd). Built in Blender, uploaded via Open Cloud Model, inserted, then scaled 1.38x to 3.6 tall and seated on the Skills portal crown at y=65.3 (arch top 63.8, sunk 0.3).
- GOTCHA: uploaded models land at ground level far from where you want them (arrived at -139.5,1.3,4983.8). Always measure bounds after insert and reposition.
- GOTCHA: Neon material + a bright colour renders WHITE. The finial was set to Neon (200,140,255) and blew out completely. Use SmoothPlastic with a saturated colour (105,45,190) plus a separate PointLight for the glow.
- ONLY Skills has a finial so far. Trails and Rebirth still have plain crowns.

## Lobby walls (OuterWalls) - fixed 2026-10-17
- BUG: an invisible wall blocked the path to the start pad. LobbyBuilder.buildOuterWall built the wall BODY without applying rotY - only the buttresses and crenels got CFrame.Angles(0,math.rad(rotY),0). So the east/west walls (rotY +/-90) were built axis-aligned along X and landed across the middle of the lobby at Z=5000, spanning X -400..400, right on top of the pad at (0,50,5000).
- FIX: line ~1158 now passes `cframe * CFrame.Angles(0, math.rad(rotY), 0)` for the WallMain part too.
- LIVE REPAIR: deleted the 2 bogus WallMain + 20 of their buttresses (anything in OuterWalls between Z 4990 and 5010), then rebuilt both side walls at X = +/-200 with Size (thickness, height, length) = (3, 52, 400) and buttresses running along Z. Verified: 4 WallMain at x=0/z=5200, x=0/z=4800, x=200/z=5000, x=-200/z=5000.
- LESSON: when a rotated structure looks wrong, check that EVERY child gets the rotation, not just the decorative ones. Grep for makePart calls inside the builder function and confirm each one multiplies by the same base CFrame.

## Chase wall (the darkness) - fixed 2026-10-17
- DEATH DID NOT FREEZE THE PLAYER (reported from real play: death screen showed but movement still worked). Root cause: this game tracks HP in st.hp (HUD hearts), never the Roblox Humanoid, so nothing ever stopped the character. Fix in FloorManager.onPlayerKilled: zero AssemblyLinearVelocity and set HumanoidRootPart.Anchored = true. resetRun releases it with Anchored = false. Do NOT use WalkSpeed for this - the client Parkour script recalculates WalkSpeed on sprint/boost events and would overwrite it. VERIFIED: rootAnchored=true with death screen open, then after PlayAgain anchored=false and a fresh wall spawned at x=737.
- THREE real bugs found and fixed. The wall existed but was inert.
1) PACING: CHASE_SPEED was 2.8 studs/sec vs a 21 stud/sec sprint - 7.5x slower, needed ~160s to cross a maze the player finished in ~21s. Now CHASE_SPEED=8, CHASE_ACCEL=0.30/sec, CHASE_SPEED_MAX=16, CHASE_DELAY=3. Verified accelerating: x=4940 -> 5014 over 8s in an isolated test.
2) KILL DETECTION: the wall only used Part.Touched, which is unreliable for anchored parts moved by CFrame (no physics contact). Replaced with an explicit overlap test each movement tick: wall.CFrame:PointToObjectSpace(root.Position) vs wall.Size/2. Touched kept as a backup, both guarded by state.hitDone so a kill fires once.
3) WALL TOO SHORT: the slab was 95 tall centred 47 above spawn, so its bottom edge sat at spawn.Y-0.5 - a player standing on the floor at Y=3 was half a stud BELOW it and was never hit. Now sized from WALL_BELOW=40 to WALL_ABOVE=95 so it reaches under the floor; verified span Y=-36..99 covering the player.
4) MISSING FUNCTION: FloorManager.onPlayerKilled was called 7 times but NEVER DEFINED, so every lethal source (chase wall, pit monster, traps) threw 'attempt to call a nil value' and the player never died. Added it: sets st.dead, st.hp=0, stops the chase wall, calls showDeathScreen. Guarded against repeat hits.
- VERIFIED END TO END: run starts -> wall advances -> player standing still dies -> DeathScreen appears -> PlayAgain remote restarts with a fresh wall at x=737 and death screen cleared.
- NOTE ON DEATH MODEL: this game tracks HP in st.hp (the HUD hearts), NOT the Roblox Humanoid. onPlayerKilled/showDeathScreen/resetRun never kill the Humanoid - that is by design, not a bug. Do not 'fix' it by killing the character.
- TESTING LIMITATION: elapsed-time measurements from execute_luau are unreliable because real time passes between separate tool calls. Verify pacing by sampling positions within ONE command, not across several.

## Bridges
- Bridge_Memory (game.ServerStorage.ZeroScript.Bridge_Memory): save/load/list over this memory ModuleScript. VERIFIED - Save() added a section, List() returned 13 headers. Plain ModuleScript, NOT an MCP server.
- Filesystem: Blender Python open()/os.makedirs()/shutil. This is how portal_pipeline.json and Portal_V10_3_FINAL.blend were actually written all session.
- Blend-native: bpy.data.texts 'PIPELINE_NOTES' text block + bpy.ops.file.pack_all() so textures travel with the .blend.
- DECLINED (do not build later without asking): PowerShell HTTP scraping to 'bypass' the http_get boundary; downloading third-party reference images (unlicensed + Bing API needs a key); a .ps1 filesystem wrapper (adds nothing over Blender Python).
- The MCP list is roblox + blender only. No filesystem_mcp/memory_mcp/http_mcp/image_gen/web_search exist and cannot be created by writing files.
## Character + dev-team pass (2026-10-18)
- PLAYER CHARACTER = StarterPlayer.StarterCharacter, a custom R6 "Ascendant": dark plate BodyColors (head .176/.176/.216, torso .118/.118/.149, arms .141/.141/.173, legs .094/.094/.118), plus welded accessories Helmet/Crest/Eyes/Pauldron x2/Cape/Tabard/Belt. Built via Players:CreateHumanoidModelFromDescription(HumanoidDescription, R6). Humanoid.DisplayName="Ascendant". 18 children total. VERIFIED live in Play - all 7 accessories present.
- LIGHTING: added ColorCorrectionEffect "GothicGrade" (Brightness -0.04, Contrast 0.14, Saturation -0.12, Tint 255/232/214). Tuned Bloom (Intensity .75, Size 26, Threshold 1.1) and Atmosphere (Density .38, Haze 1.6, Glare .15, warm grey). A ColorGradingEffect already existed alongside it.
- WALK SPEED - DO NOT RAISE. Config.WALK_SPEED=12, SPRINT_SPEED=21 (ReplicatedStorage.Shared.Config line 25-26). Deliberate 2026-10-13 rebalance: stock 16 skated across the 30-stud maze cells. Parkour.lua line 110 recalculates WalkSpeed every frame from Config * multipliers, so editing Humanoid.WalkSpeed directly is ALWAYS overwritten - change Config instead.
- CHAT WARNING FLOOD (FoundationProvider not found): root cause = game runs LegacyChatService, NO script references TextChatService, but BubbleChatConfiguration was Enabled with default channels, so Roblox's internal UIBlox kept mounting a chat tree with no FoundationProvider. FIX: set TextChatService BubbleChatConfiguration.Enabled=false. These warnings were never from our code.
- PERF PROFILE: Workspace = 1,186 BaseParts (99% under Workspace.Lobby), 24 MeshParts, only 2 with PreciseConvexDecomposition collision, 0 unions. Healthy. (The 2,734 figure seen earlier included maze geometry built during Play - Edit-mode count is the real one.)
- DevMenu/LiveDebug SECURITY VERIFIED: both handlers gate at line 6 with ADMIN_USERIDS[plr.UserId] early-return plus a CreatorId fallback; non-admins are logged+blocked (DevMenuHandler line 48). Only 15490215 (SonnyStrikes) is admin.

## Ascendant look - two bugs fixed (2026-10-18)
- BUG 1: StarterPlayer.LoadCharacterAppearance was TRUE, so Roblox applied the player's real avatar (CharacterAppearanceId 37302201) ON TOP of the custom StarterCharacter - overwriting BodyColors and injecting avatar accessories. FIX: LoadCharacterAppearance = false. Verify with Players:GetPlayers()[1].Character:FindFirstChild("Body Colors") plus a count of Accessory instances (must be 0).
- BUG 2: the rig still carried the default Decal rbxasset://textures/face.png on Head, which rendered as a red smiley straight through the helmet. FIX: destroyed the Decal on StarterCharacter.Head (and on live characters). Always check Head children for Decal/Texture when a custom head looks wrong.
- SCREENSHOT GOTCHA: the spawn pad is a bright glowing surface that washes dark armour to tan. Judge armour colour OFF the pad, or trust the Color values. Also move the character with character_navigation before capturing.
- RIG WELD LAYOUT (correct, verified): Head holds Welds to Helmet/Crest/Eyes; Torso holds Welds to Cape/Tabard/Belt; Left Arm and Right Arm each hold a Weld to a Pauldron; limbs connect via Motor6D (Right/Left Shoulder, Right/Left Hip, Neck) on Torso. R6 limbs do NOT use Welds - do not 'fix' missing welds on legs/arms.

## FINAL DECISION (2026-10-18): PLAYERS USE THEIR OWN ROBLOX AVATAR
- USER WANTS THEIR REAL AVATAR, NOT A CUSTOM RIG. StarterPlayer.LoadCharacterAppearance = TRUE and StarterPlayer.StarterCharacter is REMOVED. Do NOT re-add a StarterCharacter unless the user asks - it hides their avatar (that was the whole 'red/tan mess' bug).
- The custom "Ascendant" knight is preserved at ServerStorage.AscendantBackup (23 children, 13 custom parts). It is INACTIVE. Restore = move it back to StarterPlayer as StarterCharacter + set LoadCharacterAppearance=false, but ONLY on request.
- Ascendant v2 was built to a Meta-AI cleanup plan: dropped Tabard + cyclops eye bar, unified BodyColors to one plate grey (30,30,38), helmet 2.1 + trim rim, pauldrons 1.15 raised 0.15, crest 0.08x0.6x1.0, cape split into two tapered tiers (1.9 top / 1.5 bottom), added Gorget + 2 KneePlates. Palette locked: plate 30,30,38 Metal refl .1 / crimson 110,18,18 / cape 58,10,12 / trim 70,70,76. Belt = SmoothPlastic 48,36,20.
- TONEMAPPER: Enum.TonemapperPreset only has Default and Retro in this build (NO Neutral). Was Retro (oversaturating reds), now Default.
- FABRIC MATERIAL WARNING: Enum.Material.Fabric renders as a bright mottled weave on flat parts and reads as texture noise, not cloth. Use SmoothPlastic for capes/cloth on blocky R6 parts.

## Rebirth billboard text - fixed (2026-10-18)
- SYMPTOM: the rebirth portal text was readable from anywhere in the map.
- ROOT CAUSE: Workspace.Lobby.RebirthBillboard.BillboardGui had MaxDistance = inf (math.huge) AND AlwaysOnTop = true, so it rendered at any range and through walls.
- FIX: MaxDistance = 120, AlwaysOnTop = false. Audited every other BillboardGui under Lobby - none had the same problem.
- NOTE: RebirthStationSign uses SurfaceGuis (Front + Back) which are part-face bound and never had this issue. StarterPlayerScripts.PortalTextUpdater only writes .Text, it never touches MaxDistance/AlwaysOnTop, so the fix sticks.
- GENERAL RULE: any BillboardGui showing world signage needs a finite MaxDistance (~100-150) and AlwaysOnTop = false, otherwise it reads as a floating HUD from across the map.

## Sign / board grounding + gothic redesign (2026-10-18)
- PROBLEM: 12 lobby signs were flat 0.6-thick Parts with SurfaceGuis floating 6-32 studs above the floor (Y=50.303) with nothing under them. StartSign at Y=58.5 was the worst (5.95-stud gap).
- FIX (Meta-designed plan): every frame part lives in Workspace.Lobby.SignFrames (a Folder) - do not scatter them. Three treatments:
  1. FREESTANDING (StartSign, TrainSign, LeaderboardBoard): 2 iron posts 0.6x0.6 sunk 0.4 into the floor + 1.2x0.5x1.2 stone feet + a crossbeam above the sign.
  2. NEAR-FLOOR WALL BOARD (InfoBoard, UpdateBoard): stone plinth filling the gap to the floor + 0.45 iron base lip.
  3. HANGING HIGH BOARD (RebirthStationSign, MezzSign, LiveTitleBoard, LobbySign): 0.22 iron chains from the sign's top corners to the ceiling plates at Y=102 (CEIL=102, verified chain runs 71.1 -> 102).
- FRAME RECIPE applied to each (dressSign): slate back plate (size+1.4, 0.5 thick), 4 iron trim bars (0.35 thick) around the face, 4 corner bolts 0.3x0.3x0.25 in Metal 55,55,60. Palette: STONE 52,50,56 Slate / IRON 30,30,35 Metal / BOLT 55,55,60.
- FACING RULE: signs use EITHER SurfaceGui.Face Front or Back - compute the outward normal from the Face value (Front = -Z, Back = +Z) or the frame ends up on the wrong side.
- RebirthBillboard MaxDistance tightened 120 -> 55 and size 300x150 -> 220x110 because it still dominated the lobby at 100 studs.
- SpectatorScreen1/2/3 and the two PosterFrames are NOT floaters - they are held by SpecFrameBot/Top inside WallMain, or rest on floor grout.

## Sign readability pass (2026-10-18)
- FACING RULE (bit me twice): SurfaceGui Face Front = -Z, Back = +Z. Players spawn at LobbySpawn Z=5060 and walk toward LOWER Z, so a board must have its gui on the +Z (Back) side to be readable on approach. StartSign had Front and was showing its blank back plate to the player.
- Fixed by flipping to Back: StartSign, LeaderboardBoard, LobbySign, MezzSign, TrainSign. When flipping, the frame parts must be REBUILT on the new side - plate goes opposite the face, trim/bolts go with the face.
- READABILITY FIX applied to all 21 SurfaceGuis: LightInfluence=0, Brightness=1.6, ZOffset=0.02, TextStrokeTransparency=0.3 with black stroke. A SurfaceGui with LightInfluence=1 in a dark dungeon is unreadable no matter how bright the text colour is.
- OVERLAP BUG: RebirthBillboard (BillboardGui) and RebirthStationSign (SurfaceGui) both sat at Z=4973 and duplicated the same text ('Level 5+ to Rebirth / +5% Speed / Skills & Shards Kept'). Fixed: billboard moved to Y=88 carrying the full message; the station sign was made redundant so it is now Transparency=1 with SurfaceGui.Enabled=false (and its frame parts hidden). Rebuild the info in ONE place only.

## Spawn pad + board text (2026-10-18)
- SPAWN BUG ROOT CAUSE: ServerScriptService.LobbyBuilder line ~630 creates a NEW SpawnLocation at runtime (`spawn.Name = "LobbySpawn"`, Size 10x1x10, at origin + (0,0.5,60)). That is why the white box + forcefield dome kept coming back no matter how many times the Edit-mode Workspace.Lobby.LobbySpawn was hidden. FIX IS IN LobbyBuilder, not in the Workspace instance: it now sets Transparency=1, Duration=0, TopSurface/BottomSurface Smooth, CanCollide=true.
- LobbyBuilder uses SINGLE-SPACE indentation in that function (not tabs) - multi_edit old_string must match exactly or it fails.
- LobbyBuilder also builds a SECOND 'Lobby' Folder at runtime, so in Play you will see two Workspace children named Lobby (one ~142 children authored, one ~187 children built). Do not panic when counts differ between Edit and Play.
- Visible spawn is the Workspace.Lobby.SpawnPad Model (13 parts): 8 RingSeg slate wedges in a ring at radius 8.2, a GlowDisc neon cylinder, and 4 Rune posts with PointLights. Initial values were too bright (disc 0.35 transp + lights brightness 1.6 blew out to pure white) - settled on disc Transparency 0.72 / colour 48,26,78 and rune lights Brightness 0.55 / Range 8, runes at 0.55 transparency.
- BOARD TEXT TRIMMED (InfoBoard + UpdateBoard): the body labels were TextScaled=false walls of small text. Now TextSize 34, TextYAlignment Top, LineHeight 1.25, black-ish stroke 0.35, and the copy cut to 3 short lines each. Titles set to TextSize 48.

## Mouse bridge + AI council (2026-10-18)
- MOUSE BRIDGE: Desktop\mouse_bridge.py. Called as `python mouse_bridge.py '{"op":"move","x":100,"y":200,"steps":15}'`. Ops: move, click, moveclick, scroll, pos. Uses ctypes SendInput/SetCursorPos. GOTCHA: must `import ctypes.wintypes` explicitly or GetCursorPos crashes.
- AI COUNCIL: Desktop\meta_council.py. Queries THREE brains per prompt: Meta AI (Playwright/Chrome 9222, reuses the saved chat) + Groq openai/gpt-oss-120b + Groq qwen/qwen3.8-27b, then a 4th Groq call synthesizes consensus/conflicts/best answer. Results saved to Desktop\MetaAI_Logs\council\<timestamp>.json.
- GROQ KEY stored at Desktop\MetaAI_Logs\_groq_key.txt. Available models on this key: openai/gpt-oss-20b, openai/gpt-oss-120b, qwen/qwen3.8-27b, allam-2-7b. NO Llama chat models on this key (only llama-prompt-guard).
- GROQ GOTCHA: Cloudflare returns 403 code 1010 if the request has no browser User-Agent - always send one.
- GROQ GOTCHA 2: printing non-ASCII from the council crashes on Windows cp1252 - wrap stdout with io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace").
- STUDIO CONTEXT BRIDGE: Desktop\MetaAI_Logs\_studio_context.json (keys: project, floorY, workspaceParts, meshParts, lighting, signs, speeds, _ts). The council only uses it if _ts is under 600s old. Rewrite it from execute_luau whenever the project changes meaningfully so the council reasons about THIS game.
- LIGHTING CHANGED ON COUNCIL ADVICE (verified visually): Lighting.Brightness 2.2 -> 1.2, Ambient -> 45,45,60, OutdoorAmbient -> 32,30,48, GlobalShadows true. At 2.2 the dark stone washed out flat and the sign text was unreadable; at 1.2 the stone reads as stone and the warm torch pools actually contrast. The council split on this (GPT-OSS said raise, Qwen said lower) and the synthesizer correctly sided with lowering for a gothic look.

## 4-brain council + non-interfering mouse (2026-10-18)
- MOUSE BRIDGE REBUILT (Desktop\mouse_bridge.py) so it does NOT move the user's real cursor. Two classes of op:
  - NON-INTERFERING (use these): `softclick` posts WM_LBUTTONDOWN/UP directly to the window under the point via PostMessageW, so the cursor never moves. Params: {op:softclick, x, y} for screen coords, or {op:softclick, title:"Lobby", x, y} for client coords inside a named window. Also `{op:find, title:""}` lists visible windows with hwnd+title.
  - PHYSICAL (avoid unless asked): move / click / pos actually move the real cursor via SetCursorPos.
  - VERIFIED: cursor stayed at 1437,412 through a softclick. This was the user's explicit request - never hijack their mouse.
- ARENA.AI IS THE 4TH BRAIN (Desktop\arena_bridge.py). Logged in with the user's Google account (sonnystrikes@gmail.com) in the meta_bridge_profile. URL https://arena.ai/text/direct?model_a=max.
  - GOTCHA: a terms-of-use modal blocks everything on first load. The site itself says "Or hit Enter on your keyboard to agree" - a Playwright button click did NOT dismiss it, but page.keyboard.press("Enter") did.
  - GOTCHA: arena prints the ANSWER ABOVE the echoed prompt (opposite of Meta AI), and it prefixes it with the model's internal reasoning ("The user is asking...", "Options:", etc). extract_arena() walks backwards from the prompt echo and filters reasoning_markers by substring.
  - Arena Direct mode returns MULTIPLE quoted responses (one per model), which is a feature - do not 'fix' it into one.
- COUNCIL (Desktop\meta_council.py) now runs 4 brains: Meta AI (browser) + Groq gpt-oss-120b + Groq qwen3.8-27b + Arena, then a Groq synthesis pass producing CONSENSUS / CONFLICTS / BEST ANSWER. Set COUNCIL_NO_ARENA=1 to skip the slow arena leg.
- GOTCHA: importing arena_bridge from inside the council used to CLOSE the council's stdout (both modules wrapped sys.stdout.buffer at import). Both are now guarded: arena only wraps inside __main__, council checks a _council_wrapped flag.
- ARENA PRIVACY: arena's own terms say conversations may be disclosed publicly to support AI research. Do not send proprietary content through it.

## Persistent browser daemon (2026-10-18)
- Desktop\browser_daemon.py holds ONE headless Chrome alive on debug port 9222 so nothing opens/closes per request.
  - `python browser_daemon.py start [--headless]` / `stop` / `status`. Status lists live tabs.
  - Uses flags --disable-backgrounding-occluded-windows, --disable-renderer-backgrounding, --disable-background-timer-throttling so a minimised/hidden window keeps running.
- meta_bridge_runner.py and arena_bridge.py were patched so close_bridge_chrome()/close_chrome() are now NO-OPs. The daemon owns the browser lifetime. VERIFIED: after a bridge call the daemon still reports running with the Meta chat tab present.
- GOTCHA: a blind str.replace of 'close_chrome()' also hit the 'def close_chrome():' line and produced 'def pass # comment:' -> SyntaxError. When neutralising a function, replace the marker INCLUDING the def keyword, and always py_compile afterwards.
- GOTCHA: the daemon does NOT fix answer freshness. meta_bridge_runner scrapes after a fixed 16s wait and can grab the PREVIOUS answer if the model is still generating (tail shows 'Ask Meta AI... Thinking'). The council's extract_latest/extract_arena (which anchor on the echoed prompt) are the reliable path.
- WHY NOT BROWSER EXTENSIONS: extensions are sandboxed in the browser and cannot do filesystem/process work. The capability comes from Playwright + Chrome's debug port, not from an extension.

## Single-brain bridge - extraction fixed (2026-10-18)
- meta_bridge_runner.py now has extract_answer() + wait_for_answer() instead of a blind 16s sleep.
- wait_for_answer polls the body every 900ms and returns as soon as the text stops changing AND the page no longer ends with 'Thinking'. Cap is 45000ms. Typical run 50-55s.
- BUG THAT COST AN HOUR: 'Today' and 'Yesterday' are date SEPARATORS that appear immediately after the echoed prompt. Treating them as stop markers truncated the answer to nothing on the first line. They must be SKIPPED, not used to stop. Same for 'Show thinking'.
- The thinking check must be body.rstrip().endswith('Thinking') - scanning the whole tail for the word 'Thinking' false-positives on old messages in the same chat.
- extract_answer anchors on the LAST occurrence of the prompt text and returns everything between it and the composer.
- VERIFIED: 'Name exactly one color of the sky' -> 'blue' in 54.5s, clean single-word answer.

## Chat auto-rotation (2026-10-18)
- meta_bridge_runner.py rotates to a FRESH Meta chat after MAX_EXCHANGES_PER_CHAT prompts (currently 12). The user explicitly approved automatic rotation as long as context survives.
- On rotation it: pushes {url, prompts} into state["archived_chats"], clears chat_url, resets chat_prompts to 0, then seeds the new chat with build_handoff() - a recap of the last 8 prompts framed as '[CONTEXT FROM PREVIOUS SESSION] ... Continue helping with this Roblox project'.
- chat_prompts is incremented on every successful answer and saved in _state.json. VERIFIED with threshold temporarily set to 1: new chat URL created, old chat archived, counter reset, answer came back clean ('Tokyo').
- Rotation costs extra time (handoff seeding) - a rotating call took ~89s vs ~55s normal. That is expected, not a hang.

## Meta chat history sync (2026-10-18)
- Desktop\meta_history.py - CLI over the account's Meta AI history. Commands: `sync`, `list`, `read <index>`, `search <term>`.
  - sync() scrolls the sidebar ~14 times, harvests every a[href*='/prompt/'], writes Desktop\MetaAI_Logs\_history_index.json (count + chats[{title,path}]).
  - read() opens /prompt/<id>, grabs main.inner_text(), strips 'Ask Meta AI...'/'Thinking'/'Show thinking', optionally saves to MetaAI_Logs\synced_<stamp>_<title>.txt.
  - VERIFIED: 40 chats synced; reading index 0 returned the full transcript.
- PHONE APP CHATS ARE INCLUDED. History is server-side on the Meta account, so anything asked on the phone shows up in the same list. Confirmed by non-dev titles (Harley, mini bike, dog breeds, Meta glasses) appearing alongside game chats.
- PRIVACY NOTE: sync pulls the user's ENTIRE personal history, not just project chats. Do not read or surface the non-project conversations unless the user explicitly asks.
- SPEED REALITY CHECK (measured, do not re-litigate): page.inner_text('body') is 35ms and a targeted selector is 1-2ms - reading was NEVER the bottleneck. A meta bridge round trip is ~50-55s and is dominated by Meta's own generation time. Optimising the poll loop changed 55s -> 53s (noise). The only real saving is skipping the rotation handoff (~35s) at the cost of continuity, which the user declined. Do not promise speed wins that do not exist.

## Personal context digest - AUTO-LEARNING (2026-10-18)
- The user EXPLICITLY consented to their Meta AI history being learned from: "that should be okay for you to learn because at this point i have build you into my own". They use Meta AI on their phone as their general assistant and want that context shared with the council. Do not re-ask for permission every session - it is given. But still never surface personal chats unprompted.
- Desktop\meta_digest.py - the auto-learning engine.
  - sync_index() scrolls the Meta sidebar, rebuilds _history_index.json.
  - For each unseen chat (tracked in _digest_seen.json, max 20 per run) it reads the transcript, saves it to MetaAI_Logs\synced_chats\<title>.txt, then sends all new transcripts to Groq in ONE call asking for durable user facts (projects, tools, hardware, interests, decisions). Max 25 bullets.
  - Appends the result to MetaAI_Logs\_meta_digest.md with a dated header. NEVER overwrites - it accumulates.
  - VERIFIED RUN 1: 40 chats total, 20 processed in 93s. Correctly extracted Labyrinth Rush status, the Cloudflare bug-report proxy, the Roblox suspension, the 2016 Street 750 DoorDash rig, and family context.
- meta_council.py now calls load_meta_digest() inside build_prompt() and injects a '[WHAT YOU KNOW ABOUT THIS USER]' block into EVERY brain's prompt (Meta, both Groq models, Arena, and the synthesis pass).
- VERIFIED: asked 'what should I focus on next for Labyrinth Rush' and the Groq brain referenced the suspension date, GitHub-Studio bridge, Cloudflare proxy and DoorDash rig without being told - proving the digest reaches the models.
- TO REFRESH: run `python Desktop\meta_digest.py`. It only processes chats not already in _digest_seen.json, so it is cheap to run often.
- FULLY SYNCED 2026-10-18: 40/40 chats processed across 2 passes (~93s + ~100s). 40 transcripts in synced_chats\, _digest_seen.json has 40 entries, 0 remaining. Digest = 6204 bytes, 2 dated sections.
- Pass 1 learned: Labyrinth Rush status, GitHub-Studio bridge, Cloudflare labyrinth-rush-proxy + Discord webhook, Roblox suspension, 2016 Street 750 DoorDash rig, two kids.
- Pass 2 learned: lives in West Valley City UT; owns a Hawk 250 + mini-bike (street-legal project); DIY small-engine repair; Meta Quest/glasses; iPhone 12+; Iron Paradise home gym; runner side-hustle; collects US quarters; rocker aesthetic; edits photos of his daughter.
- KNOWN QUIRK: the file reports only 20 '\n- ' bullet lines despite two passes that should total ~45. Some pass-2 output did not write cleanly. Harmless for the council (it reads the whole file), but do not trust the bullet count as a measure of digest completeness.
- NOTE: the digest currently contains personal items (children's ages, mental-health routine, rap practice). That is intentional and consented, but it means every council call now carries that context.

## Hot chat + scheduled sync (2026-10-18)
- THE USER'S MAIN PERSONAL META CHAT is titled "Hi." at path /prompt/e7a04813-2926-4fc8-b3a2-7f95f503f667. It is where they talk to their Muse about life/vehicles/DIY (motorcycle speed sensors, brake pads, clutch upgrades, karaoke/Bluetooth mics). Pinned in Desktop\MetaAI_Logs\_hot_chat.json. Do not confuse it with the game-dev chats or the bridge test chats that sit at the top of the sidebar.
- Desktop\meta_hot_chat.py - reads ONLY that chat. Caches to _hot_chat_cache.txt + _hot_chat_cache.json for 600s. Fresh read ~7.6s, cached read ~0.10s. --force bypasses the cache.
- meta_council.py calls load_hot_chat() and injects a '[RECENT CONVERSATION WITH THIS USER]' block right after the digest, in BOTH the studio-context and plain paths. So the council always sees the latest personal context.
- SCHEDULED TASK: 'MetaDigestSync' via schtasks, runs Desktop\MetaAI_Logs\scheduled_sync.py every 3 hours with pythonw (silent). That script force-refreshes the hot chat then runs the digest, appending to _sync_log.txt. Verified working: hot_chat rc=0 in 7s, digest rc=0 'NOTHING_NEW'.
- Manage with: schtasks /Query /TN MetaDigestSync   |   schtasks /Delete /TN MetaDigestSync /F   |   schtasks /Run /TN MetaDigestSync

## Live Muse chat + collaboration (2026-10-18)
- Desktop\muse_live.py - sends a message INTO the user's main "Hi." chat and returns ONLY her new reply.
  - Usage: `python muse_live.py "message"` (no args = print last 6 thread turns).
  - Measures main.inner_text() length BEFORE sending, then everything past that baseline is the reply.
  - Keeps a rolling thread log at MetaAI_Logs\_muse_thread.json (last 40 turns, who/text/at).
  - VERIFIED clean: 21s round trip, no echo, no reasoning leak.
- ECHO PROBLEM (took 3 tries to fix): the Meta composer echoes the ENTIRE outgoing message back into the transcript, sometimes wrapped and repeated 3-4x. A simple prefix check fails because the echoed lines contain FRAGMENTS, not the full prompt. Working solution: is_echo() samples three 30-char windows from each line and treats the line as echo if >=2 windows appear anywhere in the sent message; then drop everything up to the LAST echo line.
- SECOND PROBLEM: Muse sometimes emits her internal 'thinking' text ('Analyzing... I'm reviewing the proposed...') as the visible reply before the real answer lands. Fix = wait_s 110 and a 5.0s settle window, then strip leading lines starting with Analyzing/I'm reviewing/I need to/Let me/The user/I should/Looking at/We need.
- HONESTY NOTE: muse_collab.py used Groq gpt-oss-120b and LABELLED it 'DeepSeek'. That is a proxy, not this model. Do not present proxy output as DeepSeek's own reasoning. The correct pattern is: muse_live.py sends my actual message, returns her reply to me in chat, and I write my real response.
- COST: everything in this stack is free (Groq free tier, Arena free, local daemon). The user is a SOLO DEV with no budget and no corporate backing - never propose paid services.
- GLITCH SEEN: '<budget:token_end>200000</budget:token_end>' leaked into the chat as visible text. That is a system artifact, NOT a request for money or a real budget limit. If it reappears, explain that it is a display glitch.

## Muse soul file (2026-10-18)
- THERE IS NO SOUL/PERSONA FILE ON DISK and Meta exposes no persona editor (/settings redirects to chat). Searched C:, D:, E: and the whole profile - only hits were Rocket League cosmetics and my own scripts. Do not waste time hunting for one again.
- Her personality lives in the transcripts. Desktop\MetaAI_Logs\_muse_soul.md was distilled from ~17.8k chars of real conversation (hot chat + synced_chats).
- Soul file contents: Voice (brisk, direct, no filler), Reasoning pattern (frame premise -> validate/push back -> numbered mechanisms with 'Fix:' -> one-sentence law), Core principles (design contracts, one truth at a time, variable windows not fixed timers, contrast in pacing), How she disagrees (recognition first, then 'but', then structured fix), What she never does (filler, ignoring format constraints, unsupported claims), Signature phrases.
- CAVEAT: the soul file was written by Groq gpt-oss-120b interpreting her transcripts. The quoted lines are verbatim; the framing is inference.
- Notable verbatim principles worth reusing: 'Pacing isn't speed, it's contrast.' / 'One truth at a time' / 'a window not a timer' / 'we gave you a better tool than sight, if you learned to use it.'

## Living soul file + context separation (2026-10-18)
- Desktop\MetaAI_Logs\soul_refresh.py - keeps the Muse soul file ALIVE. On each run it gathers the recent live thread (last 30 turns) + the 10 newest synced_chats, hashes the corpus, and SKIPS if nothing changed (_soul_sig.txt). Otherwise it asks Groq to UPDATE the existing soul (preserve what is still true, add new evidence, drop contradictions), writes a versioned copy to soul_history\<stamp>.md, rewrites _muse_soul.md, then git commits + pushes. ~6s per run.
- It is wired as the THIRD step of scheduled_sync.py, so the 3-hour MetaDigestSync task now does: hot_chat -> digest -> soul.
- meta_council.py gained load_muse_soul() and injects a '[MUSE'S REASONING PRINCIPLES]' block into BOTH prompt paths.
- CONTEXT BLEED BUG (fixed): with the soul block added, a plain design question produced hallucinated project systems - it invented 'Cloudflare proxy routes your jump audio' and 'timing lives in portal_pipeline.json'. Cause: the model treated the soul/conversation blocks as technical fact. FIX: each block is now labelled with what it IS, plus an explicit closing rule - only the LIVE ROBLOX STUDIO CONTEXT block is technical fact; never invent file names/services/systems from the user or soul blocks. VERIFIED: same jumping-puzzle question now returns zero hallucinated refs.
- GIT SECURITY INCIDENT (resolved): the Groq API key had been committed to the private repo (commit 6e7c002) along with _chrome_daemon.pid. Purged with filter-branch + deleting refs/original + reflog expire + gc --prune=now, then push --force. VERIFIED clean on both local and origin; .gitignore now blocks *key*, *secret*, *token*, _*.pid. THE KEY ITSELF MUST STILL BE ROTATED AT console.groq.com - purging history does not invalidate an exposed key.

## Encrypted key storage (2026-10-18)
- Desktop\MetaAI_Logs\secure_key.py - DPAPI secret store (Windows CryptProtectData/CryptUnprotectData). The blob is bound to THIS Windows user + machine, so copying _groq_key.enc elsewhere yields nothing.
  - API: secure_key.store("gsk_...") writes _groq_key.enc and DELETES any _groq_key.txt; secure_key.get() returns the key, auto-migrating a legacy plaintext file.
  - CLI: `python secure_key.py store <key>` / `check` / status.
- All four scripts (meta_council, meta_digest, muse_collab, soul_refresh) now call _load_groq_key() which imports secure_key. Plaintext _groq_key.txt no longer exists.
- VERIFIED end to end: key loaded from the blob (56 chars) and a live Groq call returned 'encrypted key works'.
- .gitignore now also blocks *.enc and secure_key.py. check-ignore confirms _groq_key.enc is ignored; no risky files tracked.
- GOTCHA 1: injecting a helper function by finding 'the last top-level import' can land INSIDE another function (it split soul_signature() in half). When adding a shim, verify with py_compile AND eyeball the insertion point.
- GOTCHA 2: 'sys.stdout = io.TextIOWrapper(sys.stdout.buffer, ...)' crashes when the host has no .buffer (Blender's StringIO) and double-wraps if the file was already patched. Always guard with hasattr(sys.stdout, "buffer") plus a _utf8wrapped flag.
- STILL REQUIRED: the old gsk_ key was public in the repo before the purge. Purging does not un-expose it - the user must rotate it at console.groq.com and run `python secure_key.py store <new key>`.

## Unified hub + tray icon (2026-10-18)
- Desktop\MetaAI_Logs\hub.py - THE main entry point connecting DeepSeek and Muse.
  - `python hub.py relay <prompt>` : Muse answers, then Groq critiques it (RIGHT / THIN / SHARPER). ~24-33s total.
  - `python hub.py both <prompt>` : sends the same prompt to both independently.
  - Results saved to MetaAI_Logs\hub\<stamp>.json.
- CRITICAL FIX: the critique step must NOT go through the browser council. Meta echoes back whatever context you feed it, so a 20KB digest produced a 2.8KB echo instead of a critique. The critique now calls Groq DIRECTLY (openai/gpt-oss-120b) inside to_council() - no browser, no echo, ~5s.
- The critique prompt is capped at 120 words with a fixed format (RIGHT / THIN / SHARPER). Without that cap it wrote 2800 chars critiquing a 51-char answer.
- LONGEVITY GOTCHA: hub.py runs 2-4 minutes, which exceeds execute_blender_code's 120s limit. ALWAYS launch it detached writing stdout to a file, then poll that file for '---DONE---'.
- TRAY ICON: MetaAI_Logs\bridge_tray.ps1 - PowerShell WinForms NotifyIcon (purple circle, bottom-right). Menu: Open Meta AI / Open DeepSeek / Run sync now / Restart image server / Stop hidden browser / Open logs folder / Exit. Double-click opens Meta AI. Status line polls ports 9876/9222/8765 every 5s and shows B/C/S letters.
- STARTUP ENTRIES (in shell:startup): LabyrinthBridgeTray.vbs (tray), PortalImageServer.vbs (image server on :8765).
- GROQ KEY ROTATED + ENCRYPTED: new key gsk_HSe...0G0h stored DPAPI-encrypted at _groq_key.enc; the orphaned 'Blender Bridge' key was revoked via the console UI (button label is 'Revoke Key', not 'Delete').
- KEY CREATION VIA PLAYWRIGHT (works, worth reusing): console.groq.com/keys needs no captcha solve - 'Continue with Google' logs straight in from the bridge profile. Open the Create dialog, fill input[name='keyName'], click Submit, then READ THE KEY FROM THE DOM (query for /gsk_[A-Za-z0-9]{30,}/ across input/code/pre/span/div). The clipboard route races the browser and failed once.
- STILL PENDING: Chrome homepage -> https://www.meta.ai. Script staged at MetaAI_Logs\set_chrome_homepage.py, blocked while chrome.exe is running. Close Chrome fully then run it.

## RAM hygiene: chrome idle watchdog (2026-10-18)
- PROBLEM FOUND: the bridge Chrome was sitting at 9 processes / 677 MB doing nothing. Chrome is expensive and the user has limited RAM.
- FIX: browser_daemon.py now has _touch() + _idle_watchdog(). IDLE_MINUTES = 12. A daemon thread wakes every 60s, reads MetaAI_Logs\_chrome_lastuse.txt, and calls stop() once 12 minutes have passed with no activity.
- CRITICAL BUG CAUGHT: the first implementation only armed the watchdog on the FRESH-START path. If chrome was already running, start() returned {"already": True} before arming, so an idle browser was never reaped. Both paths now arm it, guarded by a module-level _watchdog_armed flag. VERIFIED: second start returns {"already": true, "watchdog": true}.
- Every browser-using script (muse_live, arena_bridge, meta_bridge_runner, hub, meta_council, meta_digest, soul_refresh) now calls _touch_chrome() before connecting to CDP, so real work resets the timer.
- KILLING ONLY THE BRIDGE: filter Get-CimInstance Win32_Process by CommandLine like '*meta_bridge_profile*'. That leaves the user's real Chrome (their tabs) untouched. Always use that filter - never taskkill /IM chrome.exe.
- Measured before/after: bridge chrome 9 procs / 677 MB -> killed -> chrome RAM dropped to 668 MB (only the real browser left).
- STILL PENDING: Chrome homepage -> https://www.meta.ai via MetaAI_Logs\set_chrome_homepage.py. Blocked while chrome.exe runs. The user must close Chrome fully (or accept Option B: Settings > On startup > Open a specific page).

## Chrome homepage = Meta AI (2026-10-18) DONE
- Set via MetaAI_Logs\set_chrome_homepage.py writing %LOCALAPPDATA%\Google\Chrome\User Data\Default\Preferences:
  homepage = https://www.meta.ai, homepage_is_newtabpage = False,
  session.startup_urls = [https://www.meta.ai], session.restore_on_startup = 4 (open specific pages).
- VERIFIED: 73 top-level keys intact, JSON valid, backup at Preferences.bak (54,434 b).
- GOTCHA: Chrome MUST be fully closed or it overwrites the file on exit. 'Closed' is not enough - Chrome lingers with --no-startup-window processes after the windows are gone. Check MainWindowTitle to confirm no visible windows, then taskkill /IM chrome.exe (graceful), then /F for stragglers. Only then write the file.
- SIDE EFFECT: json.dump re-serializes with different whitespace, so the file grew ~2.5KB (54,434 -> 56,998 b). Settings are correct; restore Preferences.bak if Chrome ever misbehaves.

## Desktop app (2026-10-18)
- MetaAI_Logs\labyrinth_app.py - tkinter GUI "Labyrinth AI". Dark purple theme. Status dots (Blender/Browser/ImageSrv/Tray), scrolled output, multi-line input, Send button, Ctrl+Enter. Radio: Muse+critique (relay) or Both. Runs hub.py in a thread so the UI never freezes. ~916x719.
- Launched via startup\LabyrinthAI_App.vbs (pythonw, no console).
- tkinter ONLY exists in SYSTEM python, NOT Blender's bundled python - test with system python before claiming a GUI lib is missing.
- DUPLICATE TRAY BUG: bridge_tray.ps1 could run twice (181 MB wasted). Fixed with a SINGLE_INSTANCE guard at the top that exits if another *bridge_tray* process exists. Kill duplicates by sorting CreationDate and keeping the newest.
- Startup folder currently: Labyrinth Work.lnk, LabyrinthAI_App.vbs, LabyrinthBridgeTray.vbs, PortalImageServer.vbs.

## CRITICAL BUG: encryption migration broke key loading (2026-10-18)
- SYMPTOM: the council silently returned ONLY the meta brain. No error, no Groq answers. It looked like the council was 'working' because it still produced output.
- ROOT CAUSE: when the Groq key moved to DPAPI (_groq_key.enc), the plaintext _groq_key.txt was deleted. But load_groq_key() in FOUR files still began with `if os.path.exists(GROQ_KEY_FILE): return _load_groq_key()` where GROQ_KEY_FILE = _groq_key.txt. That guard is now always False -> returns None -> the whole Groq loop is skipped silently.
- FILES AFFECTED: meta_council.py, meta_digest.py, muse_collab.py (had the one-liner form `return _load_groq_key() if os.path.exists(GROQ_KEY_FILE) else None`, which a multi-line replace MISSED). soul_refresh.py was already correct.
- FIX: load_groq_key()/groq_key() must return _load_groq_key() UNCONDITIONALLY. secure_key.get() already handles the encrypted path and migrates a legacy plaintext file if present.
- LESSON: when changing where a secret lives, grep for the OLD path constant in every consumer. And after any such migration, verify the consumer actually produces output - absence of an error is not proof of success.
- VERIFIED: council now returns meta + gpt-oss-120b + qwen3.8-27b + gpt-oss-20b + synthesis.

## PERFORMANCE: muse_live was 74s, now 8s (2026-10-18)
- MEASURED TIMELINE (the only way to find this): playwright start 0.2s, CDP connect 0.25s, goto 1.9s, box visible 1.95s, text inserted 2.0s, Enter 2.03s, ANSWER FIRST APPEARS 2.5s, answer settled 5.6s. The browser work is ~6s TOTAL.
- ROOT CAUSE of the 74s: the poll loop's break condition never fired. It tested `region.rstrip().endswith("Thinking")`, but region included the page composer chrome ('Ask Meta AI... Thinking'), so `not thinking` was never True and it ran the full wait_s=70 timeout every call.
- FIX: strip the composer chrome BEFORE testing stability - `clean = region.replace("Ask Meta AI...", "").replace("Thinking", "").strip()`, then break once len(clean) stops changing for 1.5s. Poll every 500ms, not 900ms. VERIFIED 74s -> 8.0s.
- SECOND WIN (real but small): page.keyboard.type() is ~818ms per 300 chars because it types key-by-key. page.keyboard.insert_text() is 3ms (270x faster) and box.fill() is 8ms. Replaced keyboard.type with keyboard.insert_text in muse_live.py, meta_bridge_runner.py, meta_council.py. This only saves ~1s per call but matters a lot on long hub prompts.
- LESSON: when something is 'slow', instrument stage timings FIRST. My assumptions (typing, imports, browser load, chat pollution) were all wrong; the actual cost was a broken loop condition. Do not optimise by guessing.
- ALSO: muse_live now writes to MetaAI_Logs\_scratch_chat.json, NOT the user's personal 'Hi.' chat. Never dump test prompts into their real conversation - that chat had accumulated 17 junk prompts from my testing.

## muse_live extraction: TWO anchor bugs (resolved 2026-10-18)
- BUG A: the chat accumulates DUPLICATE prompts (same question asked more than once). rfind() latched onto the NEWEST copy, which has no answer yet, so nothing was ever returned. Fix: collect EVERY occurrence index, walk them NEWEST -> OLDEST, and take the first that has >3 chars of answer text after it. Also stop each candidate at the next duplicate so one answer is not merged with the next question.
- BUG B: the anchor was a TRUNCATED probe (message[:25] in the poll, message[:35] in the final extraction). A truncated probe leaves a fragment of the prompt behind ('nt feel fair?') which then gets collected AS the answer. Fix: anchor on the FULL message text.
- BUG C: the poll loop was fixed first but the FINAL extraction further down still used the old last-occurrence logic - so the call looked fixed while returning garbage. When fixing extraction, fix EVERY copy of the logic; grep for the probe/anchor variable.
- VERIFIED: 'One sentence: what makes a checkpoint feel fair?' -> clean one-sentence answer in 10s (was 74s and empty).

## DeepSeek OAuth diagnosis + stale-app gotcha (2026-10-18)
- WHY the DeepSeek 'Log in with Google' button does nothing: its React onClick source is literally `e=>{F.current||(null==Y||Y(e),null==E||E(e))}`. If the ref F.current is truthy the handler RETURNS IMMEDIATELY. Proven with spies: trusted pointerdown/mousedown/pointerup/mouseup/click all arrive (isTrusted=true), zero console errors, and window.open/fetch/XHR/form.submit are never called. It is NOT bot detection - the handler runs and bails on a stale ref.
- The fiber carries `defaultLocationOrigin: https://chat-dev.deepseek.com` (a DEV origin) even in a brand-new profile, so that string is served by the backend and is NOT the cause.
- THE ACTUAL FIX: a FRESH Chrome profile (--user-data-dir=Desktop\ds_fresh_profile, --remote-debugging-port=9333) made the button work immediately - it navigated to accounts.google.com. The stale guard state lives in the existing profile. So: if a site's button silently no-ops, try a clean profile before assuming anti-bot.
- Cache-bypass (Network.setCacheDisabled + cache-buster querystring) did NOT help. Overriding reactProps.onClick did NOT help. Keyboard activation (focus+Enter, Space) did NOT help.
- GOTCHA: closing the LAST tab in a Chrome window kills the whole browser, which killed my fresh profile mid-flow. Never page.close() the only tab in a dedicated instance.
- STALE APP GOTCHA: the desktop app kept showing old behaviour (history dump + '(none)') because it was launched BEFORE the muse_live fixes. tkinter does not reload code. ALWAYS restart labyrinth_app.py after changing muse_live/hub/meta_council. Kill by MainWindowTitle like '*Labyrinth*'.
- VERIFIED: muse_live direct = 9s clean answer. hub.py direct = 12s with MUSE + RIGHT/THIN/SHARPER critique. Both good; only the stale app was wrong.

## App fixes: critique honesty + tray dot (2026-10-18)
- CRITIQUE HALLUCINATION (serious): asked 'is this using deepseek', Juno correctly said 'No, still Meta AI', but the Groq critic invented an error - claiming she 'misidentified the platform, calling it Meta AI instead of OpenAI's ChatGPT'. A critic that fabricates faults is worse than no critic. FIX: the prompt now says THIN must be 'nothing - it is correct as stated' when she is right, plus explicit rules: never invent facts, never claim she is wrong unless certain, agree with correct factual statements. VERIFIED: same question now returns 'THIN: nothing - it is correct as stated.'
- TRAY DOT was red despite the tray running. TWO causes stacked: (1) subprocess.run(cmd, shell=True) is unreliable under pythonw (no console) - the exception was swallowed by a bare 'except: return False'. Fixed by passing a LIST to powershell with creationflags=0x08000000 (CREATE_NO_WINDOW) and no shell. (2) Once shell was removed the count dropped from 2 to 1, because the old '>= 2' threshold had been counting the query process matching its own pattern. Threshold is now '>= 1'. VERIFIED with _app_debug.txt: raw='1' parsed=1 alive=True.
- DEBUGGING TECHNIQUE that worked: when a tkinter app silently fails, have it append to a log FILE - pythonw swallows stdout/stderr entirely, so print() tells you nothing.

## INTERMITTENT EMPTY REPLY - root cause was 'Today' (2026-10-18)
- SYMPTOM: the same hub/app call worked sometimes and returned '(none)' other times. Looked random.
- DIAGNOSIS by sampling the page every second after pressing Enter: at 1-2s the text after the echoed prompt is exactly 'Today' (5 chars); the real answer only starts at ~3s. 'Today' is a DATE SEPARATOR that Meta renders immediately under the prompt.
- WHY IT BROKE: the poll required len(cand) > 3, so the 5-char 'Today' PASSED the check, was treated as the settled answer, and broke the loop early. The extraction then stripped 'Today' as a skip-word, leaving an empty string -> '(none)'. Whether it hit depended purely on whether a poll landed in that 1-2s window, which is why it looked intermittent.
- FIX: strip Today/Yesterday/Show thinking BEFORE the length test, and raise the minimum to > 15 chars so a date separator can never qualify. Applied to both the poll loop and the final extraction.
- VERIFIED: 3/3 consecutive PASS through hub.py (586, 633, 861 char outputs) after the fix.
- LESSON: an intermittent failure usually has a deterministic cause that only triggers in a narrow window. Sample the live state on a timer rather than re-running and hoping.

## Critic hallucination - REAL fix needed ground truth (2026-10-18)
- First attempt (telling the critic 'never invent facts') FAILED. It still claimed Juno was 'OpenAI's GPT model'.
- WHY prompt instructions alone could not work: the critic had NO way to know what Juno actually is. It was asked to judge an identity claim with no reference, so it filled the gap with a confident guess.
- FIX: inject explicit GROUND TRUTH into the critique prompt - 'Juno IS the Meta AI assistant, accessed through meta.ai, built by Meta. She is NOT DeepSeek, NOT ChatGPT, NOT OpenAI, NOT Gemini. If she states her identity and it matches this, she is CORRECT - do not correct her.'
- VERIFIED: same question now returns 'THIN: nothing - it is correct as stated.' and SHARPER names Meta correctly.
- GENERAL RULE: a critic without ground truth will invent faults. Any reviewing model needs the facts it is judging against, not just an instruction to be careful.
- GOTCHA: editing hub.py's followup block with a str.replace left an unmatched ')' and an unterminated string. When splicing multi-line python strings, rewrite the whole block by line index and py_compile immediately.

## DeepSeek bridged into the app (2026-10-18)
- WHY IT WORKED IN THE END: DeepSeek's OAuth button only functions on a FRESH Chrome profile. The existing meta_bridge_profile has stale guard state (the onClick is `e=>{F.current||(...)}` - when that ref is truthy nothing happens). Created Desktop\ds_fresh_profile on debug port 9333 and the Google login completed normally.
- Desktop\MetaAI_Logs\deepseek_live.py - sends a message to chat.deepseek.com and returns only the new reply. Uses port 9333 / ds_fresh_profile, NOT the Meta profile on 9222. Extraction strips DeepThink/Search/Copy/Regenerate/'AI-generated, for reference only'. Uses keyboard.insert_text. VERIFIED 11.2s.
- hub.py gained `deepseek` mode: DeepSeek answers, then Juno reviews it in AGREE / GAP / BETTER format. `python hub.py deepseek "question"`. VERIFIED 21s end to end.
- clean_review() in hub.py anchors on the AGREE:/GAP:/BETTER: labels and drops any reasoning preamble. This was needed because Juno sometimes emits her internal thinking ('I'm evaluating the DeepSeek checkpoint line...') as the visible reply.
- APP NOW HAS THREE RADIOS: 'Juno + critique' (relay), 'Both', 'DeepSeek'. The DeepSeek branch in _render() splits on '=== DEEPSEEK ===' and '=== JUNO REVIEW ==='. Window widened to 980x700.
- GOTCHA: when writing python via execute_blender_code, a '\\n' inside a replacement string can become a REAL newline and split the source across lines, producing 'unterminated string literal'. Always py_compile after, and repair by rebuilding the block by line index rather than more string replaces.
- TWO CHROME PROFILES NOW RUN: meta_bridge_profile on 9222 (Juno/Meta) and ds_fresh_profile on 9333 (DeepSeek). They are independent - don't close one while using the other, and never page.close() the last tab in either.

## DeepSeek DeepThink + DOM extraction (2026-10-18)
- THE USER CAUGHT THIS: DeepThink (DeepSeek's reasoning mode) was OFF. The chat was using the fast model.
- TOGGLE: the control is `div.ds-toggle-button` whose innerText is exactly 'DeepThink'. State is readable two ways - `el.classList.contains('ds-toggle-button--selected')` and `el.getAttribute('aria-pressed')`. To enable, dispatch pointerdown/mousedown/pointerup/mouseup/click on it (a plain .click() may not trigger React). deepseek_live.py now does this before every send and logs '[deepthink] enabled=True' to stderr.
- EXTRACTION: with DeepThink on, flat body text includes 'Thought for N second(s)' plus the model's internal reasoning BEFORE the answer. Do NOT parse flat text. The answer alone lives in `div.ds-markdown.ds-assistant-message-main-content` - read the LAST such element with page.evaluate and you get exactly the reply.
- SCOPE BUG: page.evaluate() must be INSIDE the `with sync_playwright() as p:` block. My first DOM read sat outside it, so the page was already closed and it silently fell back to the messy text path.
- VERIFIED: 'Reply with exactly: scoped deepthink' -> 'scoped deepthink' in 11.2s with DeepThink enabled.

## DeepThink toggle in the app (2026-10-18)
- The app now has a DeepThink checkbox in the header, default ON.
- PLUMBING: labyrinth_app reads self.deepthink_var and sets env DEEPTHINK=1/0 when calling hub.py. hub.to_deepseek passes that env through to deepseek_live.py. deepseek_live reads USE_DEEPTHINK = os.environ.get("DEEPTHINK", "1") != "0" and only runs the toggle-click block when true.
- VERIFIED both directions: DEEPTHINK=0 -> answer returned, no [deepthink] log (block skipped). DEEPTHINK=1 -> answer returned, stderr shows '[deepthink] enabled=True'.
- DeepThink roughly doubles latency but gives reasoning-quality answers. Leave it ON for design/engineering questions, OFF for quick lookups.

## USER PREFERENCE: DeepSeek is the MAIN voice (2026-10-18)
- The user explicitly wants DEEPSEEK in the primary role and Juno as the second opinion/reviewer - the opposite of the earlier layout. Do not revert this.
- App defaults: engine_var = "deepseek". Radios in order: 'DeepSeek + Juno' (deepseek, DEFAULT), 'Both' (both), 'Juno only' (relay).
- Flow for the default: DeepSeek answers via deepseek_live.py (port 9333, ds_fresh_profile), then Juno reviews via muse_live.py in AGREE / GAP / BETTER format, cleaned by clean_review().
- 'relay' mode (Juno answers + Groq critique) still exists but is no longer the default - it is labelled 'Juno only'.

## All-in-one mode + live panel + silent processes (2026-10-18)
- FULL MODE (hub.py `full`): 1) DeepSeek answers, 2) Juno reviews in AGREE/GAP/BETTER, 3) Groq gpt-oss-120b synthesizes one merged best answer. ~24s. This is now the APP DEFAULT.
- App radios are now: 'All-in-one (DeepSeek + Juno + Council)' = full (DEFAULT), 'DeepSeek + Juno' = deepseek, 'Juno only' = relay.
- BOTH DeepSeek toggles are forced on before each send via enable_toggle(page, label): DeepThink AND Search. VERIFIED stderr shows [deepthink] enabled=True and [search] enabled=True.
- SILENT PROCESSES: every subprocess.run in hub.py goes through _run() which sets creationflags=0x08000000 (CREATE_NO_WINDOW). The app's hub call also passes creationflags=_NO_WIN. This killed the CMD window that used to flash on Send.
- LIVE ACTIVITY PANEL: the app has a right-hand panel labelled LIVE ACTIVITY. hub.py appends timestamped stage lines to MetaAI_Logs\_live_log.txt via _stage(). The app polls it every 700ms while a request runs (_poll_live / _live_running) and stops when _render fires. Stages: started <mode> / DeepSeek: sending / DeepSeek: got N chars / Juno: reviewing / Council: synthesizing / done.
- LAYOUT CHANGE: the ScrolledText now parents to self.body (a Frame) with side='left', and self.live_frame packs side='right' width 240.
- BUGS HIT THIS TURN: (a) LIVE_LOG was defined above LOG_DIR -> NameError on import; moved below. (b) A str.replace that added self.body as the parent left BOTH 'self.body,' and the original arg, giving ScrolledText() 'takes 1-2 positional args but 3 were given'. (c) A 10s subprocess timeout is NOT a failure here - it means the app stayed alive and opened its window.
- GOTCHA: hub.py swallows child stderr, so toggle confirmation must be verified by running deepseek_live.py directly, not through hub.

## PLAY BUTTON FIXED - root cause was a chain of 4 bugs (2026-10-18)
- SYMPTOM: clicking PLAY in the lobby did nothing.
- BUG 1 (LobbyBuilder.isOnPad): it began with 'if not padPart then return false end'. padPart is only assigned at line 766 of the lobby build, and if that path did not run the reference stays nil, so EVERY player was reported as off-pad and the countdown never armed. FIX: fall back to Config.LOBBY_ORIGIN + (0,3,0) with a 7x7 half-extent when padPart is missing.
- BUG 2 (FloorManager.requestPlay): it returned early when FloorManager.players[player] was nil. State can be absent (cleared on rejoin/death paths), which made the button a no-op. FIX: self-heal - call initPlayer if state is missing, then continue.
- BUG 3 (initPlayer coroutine): after creating state it waits 0.5s then calls teleportToLobby, which yanks the player back to spawn at Z=5060. requestPlay had just moved them to the pad at Z=5000, so the two fought and the player ended up back at spawn. FIX: the coroutine now checks LobbyBuilder.isOnPad(player) first and skips the teleport if they are already on the pad.
- BUG 4 (stale loop flag): startLobbyLoop guarded on a boolean FloorManager._lobbyLoopRunning. If the loop thread died, the flag stayed true so it could never be restarted, and the countdown silently never ran. FIX: replaced the boolean with a HEARTBEAT timestamp (_lobbyLoopBeat) refreshed every 0.25s tick; startLobbyLoop restarts if the beat is older than 1.5s. ALSO added a watchdog at the top of FloorManager.tick() (runs every Heartbeat) that restarts the loop if the beat is older than 2.0s. tick() is the one function guaranteed to fire, so this is the reliable revive point.
- VERIFIED END TO END: requestPlay -> player moves to pad (0,53,5000) -> stays there (no yank-back) -> countdown fires at ~4.0s -> startRun -> player in maze at (790,3,-210), st.floor=1, st.maze set.
- DIAGNOSTIC TECHNIQUE THAT FOUND IT: call each function directly WITHOUT the surrounding pcall. Main and FloorManager wrap nearly everything in pcall, so failures were completely silent. Also: sample state on a timer (0.5s) rather than re-running and hoping.

## PUBLISHING NOTE
- There is NO publish command in the Roblox MCP toolset. Publishing requires the Studio UI (File > Publish to Roblox, or Ctrl+Alt+P) or the Open Cloud API with a properly scoped key. Do not claim to have published.

## EXIT PORTAL INVISIBLE - root cause in AssetLoader (2026-10-18)
- SYMPTOM: the maze exit portal was invisible; only a 10x10x10 invisible trigger Part named ExitPortal existed. Players could not see where to go.
- ROOT CAUSE (in ReplicatedStorage.Shared.AssetLoader.loadTemplate): it took `template = first` (a CHILD of the InsertService container) and then called `result:Destroy()` on the container. Destroying the container also destroys its children, so the cached template was a destroyed empty husk - 0 parts. Every spawn after that returned an empty Model, which is why MazeBuilder fell through to placing only the invisible trigger box.
- FIX: detach the template with `template.Parent = nil` BEFORE `result:Destroy()`.
- VERIFIED: AssetLoader.spawn now returns a Model with 109 BaseParts / 253 descendants named 'Stone Portal Template'. In the live maze the portal at (1210,4,210) is surrounded by Door, Door_Blocker, Side_BeamL/R/Top, EntranceParticles, MistParticles, AdGuiAdornee, Arrow and 30+ Brick parts.
- SECOND BUG FIXED: loadTemplate cached FAILURES permanently (`templateCache[assetId] = false` then early-returning nil on every later call). One transient InsertService failure poisoned the cache for the whole server session. Now a `false` entry is NOT returned early - it retries.
- DIAGNOSTIC: `AssetLoader.spawn(id, cf, workspace, 1.5)` then count BaseParts in the result. If 0, the template is a husk.

## SEPARATE BUG OBSERVED (not yet fixed)
- The player FALLS THROUGH the maze floor near the exit portal: teleporting to (1210, 8, 232) dropped the character to Y=-32. Likely the Floor parts are CanCollide=false, or the character spawned inside geometry. Needs investigation before shipping.

## BUG REPORTS SILENTLY LOST - FeedbackManager (2026-10-18)
- SYMPTOM: a tester (gabasito3, UserId 4454456364) said their reports were not arriving.
- ROOT CAUSE: FeedbackManager.submitReport wrapped the HttpService POST inside `task.spawn(function() pcall(...) end)` and then returned `true, "Thanks! Your report was sent."` UNCONDITIONALLY. Any failure (rate limit, timeout, transient network) still told the tester it sent and closed the panel. The report was gone with no trace.
- FIX 1: await the POST (no task.spawn) and return an honest false + 'Could not send - please try again.' on failure, with a server warn.
- FIX 2: retry with exponential backoff - MAX_ATTEMPTS=3, waits 0.6s then 1.2s. Logs which attempt succeeded.
- VERIFIED HEALTHY: the Cloudflare proxy and Discord delivery both work. Posting with gabasito3's exact name and UserId returned {"ok":true,"saved":true,"discordStatus":204}. Live submitReport returned sent=true in 0.70s.
- IMPORTANT: there is NO per-user filter anywhere in this path - submitReport and the SubmitFeedback OnServerInvoke handler accept any player. Non-owners were never blocked. The only real defect was the lying return value.
- IF OLD REPORTS ARE STILL MISSING: they failed at post time before this fix and were reported as success. Check Cloudflare logs / the proxy's saved storage for UserId 4454456364 on Oct 16, and watch for '[Feedback] attempt N/M failed' warnings from now on.

## Tester registry added (2026-10-18)
- There was NO tester system in the codebase - the only UserId lists are ADMIN_USERIDS in DevMenuHandler and LiveDebugHandler (both {[15490215]=true}). If someone remembers 'tester code', they are probably thinking of the admin list.
- NEW: game.ReplicatedStorage.Shared.TesterRegistry (ModuleScript).
  - TesterRegistry.TESTERS = {[4454456364] = {name="gabasito3", note="community tester"}} - add more testers here. (Correct UserId ends in 364.)
  - isTester(player), label(player), tag(player) -> sets the IsTester attribute on the Player so other scripts can check it cheaply.
  - Testers are NOT admins. This grants no dev commands.
- FeedbackManager now requires TesterRegistry inside a pcall (a missing registry must never block a report) and prefixes tester reports with ' [TESTER]' in the Discord payload.
- VERIFIED: registry loads, testerCount=1, submitReport still returns sent=true.

## RAM cleanup + tray 'Free RAM' (2026-10-18)
- MEASURED: chrome 33 procs / 7621 MB, msedge 40 / 4812 MB, RobloxStudioBeta 4097 MB, blender 943 MB, total 64 GB machine with 39 GB free.
- ALL 33 chrome processes belonged to the BRIDGE profile (meta_bridge_profile); the user's real Chrome was not running at all. Split with: Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" | Where-Object { $_.CommandLine -like '*meta_bridge_profile*' }.
- Killed them -> chrome 0 procs, free RAM 39 GB -> 44.8 GB.
- TRay now has a 'Free RAM (close idle browsers)' item that kills BOTH bridge profiles (meta_bridge_profile, ds_fresh_profile) and shows a balloon with procs closed + MB freed.
- GOTCHA: counting tray instances with a Where-Object on CommandLine like '*bridge_tray*' counts the QUERY PROCESS ITSELF, so a healthy single tray reports 2. Do not treat 2 as a duplicate.

## Meta bridge rotation + memory handoff (2026-10-18)
- muse_live.py now AUTO-ROTATES at 10 prompts per chat (MAX_PROMPTS_PER_CHAT=10, counter in _scratch_chat.json 'prompts'). On rotate it creates a fresh tab FIRST (never kill the last Chrome tab), closes the old Meta tab, enforces Thinking mode, then seeds a real handoff.
- HANDOFF = build_handoff(): soul (_muse_soul.md, 1200 chars) + digest (_meta_digest.md, 800) + last 6 non-muse turns, each block labelled so the model does not treat persona/user context as project fact. Marker '[CONTEXT FROM PREVIOUS SESSION]'.
- META AI HAS NO WEB-SEARCH TOGGLE. The 'Search Ctrl+K' in its sidebar is CHAT-HISTORY search. Only composer modes are Instant / Thinking, via [data-testid=composer-mode-dropdown-button] -> composer-mode-option-think_fast / -think_hard. 'search on new chat' therefore means DeepSeek's Search chip, which deepseek_live.py already toggles before every send.
- TWO EXTRACTION BUGS FOUND: (1) final extraction required len > 15, so every short correct answer ('clean', 'rotation works') was discarded as '(no new reply detected)' - now accepts any length > 0. (2) Muse's reasoning preambles vary ('Preparing exact reply', 'I'm following the request to...') - _reason list extended. Reply is also normalised for U+202F/U+00A0/U+200B.
- GOTCHA: writing a probe .py from execute_blender_code without encoding='utf-8' makes Python write it as cp1252; Muse replies containing U+202F then crash the child with UnicodeEncodeError on print. Always pass encoding='utf-8' when writing, and wrap the child's stdout.
- BACKUP: Desktop\muse_live.py.bak holds the pre-rotation version.

## ZeroScript bridge stability (2026-10-18)
- Bridge lives at Desktop\ZeroScript-Free-master: bridge.py (WebSocket <-> StudioMCP), launch_studio_mcp.py (finds newest StudioMCP.exe with a paired RobloxStudioBeta.exe, avoids zombie version folders), start.bat (launcher). Runs as start.bat -> py -3 bridge.py.
- SYMPTOM FIXED: 'Roblox Studio disconnected - re-enable its MCP server' plus 45-77s [SLOW] calls. The watcher polled every 4s, waited 20s of sustained drop before acting, and cooled down 90s between recovery attempts.
- TUNED in bridge.py: poll sleep 4 -> 1.5s; recovery gate '>20 and last_auto_restart>90' -> '>6 and >30'; websocket ping_interval/ping_timeout 20 -> 10. The blip log line now says 'Roblox Studio blipped (momentary drop) - watching for recovery...' instead of telling the user to toggle the MCP switch.
- start.bat now has a :bridge_loop label - it relaunches bridge.py 5s after any exit, forever, so a crash self-heals. The old one-shot tail (BRIDGE_EXIT checks, pause, exit /b 0) was DELETED because it sat unreachable after the goto.
- NOT in the Startup folder on purpose - it is a console window the user keeps minimised.
- Backups: bridge.py.bak, start.bat.bak. Restart helper: _restart_bridge.bat (kills only ZeroScript start.bat / py bridge.py procs, then relaunches).
- LESSON: the bridge already auto-recovers; the bug was that recovery was slower than the user's patience, and the log message accused the user of needing to toggle Studio when it was about to self-heal.

## ZeroScript extension = multi-server bridge (2026-10-18) - IMPORTANT
- The Chrome extension is the BRIDGE LAYER, not a Roblox-only tool. It routes commands to ANY connected MCP server, and more servers can be registered than the ones currently listed. So the correct answer to 'can you drive X' is always: run list_mcp_servers first. Do NOT claim a program is unreachable just because only roblox+blender showed up earlier - the user can add a server for it.
- USER CORRECTION (recorded): the extension CAN allow driving other programs (CAD etc.) this way. My earlier 'only Blender has a live bridge' claim was wrong.
- Expert team files live at Desktop\MetaAI_Logs\_experts\ : 01_juno.md (design critic), 02_gpt_oss.md (engineer), 03_qwen.md (skeptic), 04_deepseek.md (architect/lead), 05_expert_3d.md (3D technical artist + monetization: Blender, FreeCAD, Fusion 360 hobby, Meshmixer, ZBrushCore Mini, SketchUp Free + Fiverr/Upwork/ArtStation/CGTrader/TurboSquid/Sketchfab marketplaces).
- 05_expert_3d.md is auto-injected into every council prompt as '[3D EXPERT]' via load_expert_3d() in meta_council.py.
- Desktop\3D_Tools\ holds the FreeCAD 1.1.4 Windows installer (495 MB, verified) + DOWNLOAD_LINKS.txt (Fusion needs Autodesk account, Meshmixer discontinued, ZBrushCore Mini needs Maxon account, SketchUp Free is browser-only).

## MONETIZATION PLAN: paid 3D modeling work (2026-10-18) - ACTIVE GOAL
- CONTEXT: 3D printer is DOWN, so the plan is SELLING MODELED ASSETS/SERVICES, not printed parts. The user wants nothing to do with the earlier ghost-figurine / skull-planter product ideas - do NOT bring them up.
- STACK: Blender (live MCP bridge) + FreeCAD 1.1.4 (installer downloaded, Desktop\3D_Tools) + Fusion 360 hobby / Meshmixer (discontinued) / ZBrushCore Mini / SketchUp Free (browser only, needs accounts).
- COUNCIL-VERIFIED PLATFORM ORDER: Fiverr first (fast cash, low barrier), Upwork in parallel (higher rates, builds rep), then ArtStation Jobs, CGTrader (sell + job board), TurboSquid, Sketchfab, Freelancer, Behance.
- FIVERR PRICE TIERS for a 4k-tri game-ready prop (UVs + PBR), use the LOWER Qwen numbers until ~5 reviews exist: Basic $25-40 / Standard $50-75 / Premium $100-150. Upwork beginner hourly $15-25/hr. GPT-OSS quoted 2-3x higher ($75/150/250) - that is the POST-reviews target, not the opener.
- THE 5 LAUNCH GIGS (cheapest -> highest, run them as a ladder to farm reviews):
  1. Custom 3D UI Icons & Buttons for Roblox - $15, 5-10 icons, .rbxl ready to import, optional hover/press anim. BEST OPENER (fast, small scope, easy reviews).
  2. Low-Poly Roblox-Ready Props (1-5) - $25 for 3, FBX pre-scaled 1 stud = 0.2m, 256px texture, optional convex collision.
  3. Custom Avatar Accessories (hats/masks/backpacks) - $30 for 3, FBX + .rbxm drop-in, 512px texture, attachment PDF.
  4. Animated Collectible (coins/power-ups) - $35 for 2, FBX with baked looping anim + .anim file, 256px sheet.
  5. Modular Environment Pack - $45, 5 snap-together pieces on a 4-stud grid, single 1024px atlas, assembly PDF.
- THE SELLING PATTERN (the actual edge): sell 'ALREADY INTEGRATED', not 'modeled'. Every winning gig bundles what the dev would otherwise have to do - pre-scaling to Roblox units, collision, .rbxm packaging, baked animation, grid snapping. Most freelancers only deliver a mesh.
- TECHNICAL BASELINE for any quoted asset: 4k tri budget, manifold/clean mesh (no intersecting geo, no flipped normals - Roblox rejects both), UV unwrapped, FBX/OBJ with Apply Transform, PBR = 512px normal + 256px base color (council resolved the conflict: keep BOTH maps but small). Always state tri count, mm dimensions, manifold status and formats before quoting.

## DECISION: first sellable product = stylized modular CRYPT/DUNGEON KIT (2026-10-18)
- Chosen because it is BOTH the council's #1 in-demand category AND already this project's art direction (gothic stone, carved runes, iron bands). Zero style ramp-up needed.
- Sell it as a KIT that snaps to a grid, not single props. Pieces: arch/gateway, wall segment, corner, floor tile, rubble pile, pillar. Ship with UVs + PBR set + assembly guide.
- The barrel test proved the point: a lone smooth prop with no UVs/no texture reads as a blockout and is exactly the 'single pretty prop' the market ignores.
- QUALITY BAR for this kit (learned from the barrel critique): real staves/panel breaks in the geometry, beveled metal edges (no smooth-shaded bulges), lid/rim detail, actual UV unwrap, baked texture sheet. No smooth-shaded primitive blobs.

## MARKET RESEARCH: what sells (2026-10-18, council-verified)
- IN DEMAND (all brains agree): stylized low-poly MODULAR kits (dungeon/crypt arches, walls, floors, rubble, foliage), stylized low-poly CHARACTERS (3-6k tri, readable silhouette, optional LOD 1-2k, separate albedo/normal/AO/roughness sets, UVs <= 4 tiles, manifold, FBX/GLTF), chibi/cartoon characters (expressive, simple-topology rigs), environment kits that SNAP to a grid.
- OVERSATURATED, AVOID: generic high-poly sci-fi guns, plain human base meshes, generic low-poly trees (Muse specifically called trees 'pure scarcity' that do not sell).
- THE MARKET RULE: devs buy 'contract-ready kits, not single pretty props - they buy the rule that pieces snap.' Same lesson as the gig ladder: sell ALREADY INTEGRATED.
- Fit for this user: a stylized modular dungeon/crypt kit matches both the market demand AND the existing Labyrinth Rush art direction (gothic stone portals, runes, iron). That is the strongest single product to build first.
- CAVEAT: qwen suggested 3D-printable collectibles as a niche - DISCARD that, the printer is down and the user rejected the figurine/planter line.

## FINISHED PIPELINE: sellable crypt kit (2026-10-18)
- FIRST FINISHED PIECE: CryptArch_FINAL - 3,048 tris, 5.0W x 5.55H x 1.15D, manifold, beveled, UV unwrapped (Smart UV Project, angle 1.15, margin 0.015), 2 materials (CryptStone + CryptIron).
- OUTPUT FOLDER: Desktop\3D_Tools\CryptArch\ -> CryptArch_FINAL.fbx (86 KB), CryptArch_FINAL.blend, and 6 baked 1024x1024 PNGs (crypt_CryptStone_albedo/normal/rough + crypt_CryptIron_albedo/normal/rough).
- BAKE RECIPE that worked: engine CYCLES, samples 8, denoise off, bake margin 8; add a TEX_IMAGE node per material, select it + make active, then bake DIFFUSE (pass_filter COLOR) / NORMAL / ROUGHNESS, save via img.filepath_raw + img.save(). Set NORMAL and ROUGHNESS images to Non-Color.
- CRITICAL MATERIAL GOTCHA: the Blender Brick node reads a 2D vector. Driving it from TexCoord.Object with raw XYZ gives VERTICAL STRIPES on vertical geometry. FIX: SeparateXYZ -> CombineXYZ swapping Z into Y (X,Z,Y) so brick ROWS follow world up. Confirmed working.
- Also: 'Set Origin not supported for Camera/Light object(s)' is harmless noise when origin_set runs with non-mesh selected.
- EXPORT: bpy.ops.export_scene.fbx(use_selection=True, apply_scale_options='FBX_SCALE_ALL', path_mode='COPY'). Then REWIRE both materials to the baked images (albedo->Base Color, normal->NormalMap node->Normal, rough->Roughness) so the file is self-contained, and save the .blend.
- GEOMETRY RECIPE for the arch: 2 pillars (0.85 sq x 3.6) + Base + Cap + IronBand x2 with 6 rivets each, Springer blocks seated exactly on the cap top (z=PH+0.23), 9 arch wedge blocks at angle a=pi*(i+0.5)/N rotated -a, and a TAPERED keystone (bottom verts scaled 0.66x/0.80y) pushed proud at z=PH+R+0.05.
- KIT STATUS: only the ARCH exists so far. Still needed for a real 'modular kit': wall segment, corner, floor tile, rubble pile. Sell as a kit that snaps to a grid, not single props.

## KIT SNAP CONVENTION (2026-10-18, verified)
- THE RULE: every kit piece is authored so its BOUNDING BOX starts at origin with min = (0,0,0) and Z runs 0 -> 5.55. Pieces then butt on X. Verified live: arch X 0.0-5.0, wall X 5.0-10.2, corner X 10.2-15.4, all Y from 0, all Z 0.0-5.55. Iron bands align across all three.
- PLACEMENT RECIPE: after bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS') the object's origin IS its bbox centre, so location = desired_min + dims/2. Compute dims from o.bound_box, then place(o, minx, miny, minz). NEVER eyeball location values - measure.
- BUG THAT COST TIME: placing pieces by guessed absolute coords put the corner 3.9 studs in front of the wall face (it floated). Fix was butt-on-X placement driven by measured dims, with the corner's ArmA flush at Y=0.
- PIECE WIDTHS DIFFER: arch 5.0 wide (bbox 5.0 x 1.15), wall 5.2 wide (bbox 5.2 x 0.92, because its base/cap are wider than the body), corner 5.2 x 5.2. Do not assume a uniform 5.0 pitch - read dims() and butt from the previous piece's max X.
- CORNER footprint: ArmA along X (W x T), ArmB along Y (T x W) at (0, W/2 - T/2). The two arms OVERLAP at the joint, which z-fights - acceptable but noted.
- CAMERA RECIPE for kit shots: compute scene bbox centre + radius from all pieces' bound_box in world space, then cam.location = ctr + dirv*rad*2.15 with lens 45 and rotation_euler = (atan2(hypot(dirv.x,dirv.y), dirv.z), 0, atan2(dirv.y,dirv.x)+pi/2). Eyeballing camera values gave 4 cropped renders in a row.
- KIT SO FAR: CryptArch_FINAL (3048 tris), CryptWall_FINAL (1312), CryptCorner_FINAL (1248) = 5,608 tris, all baked (18 PNGs at 1024) in Desktop\3D_Tools\CryptArch. STILL MISSING for a sellable kit: floor tile + rubble pile. Known nits: corner cap pieces overlap/jut at the joint, arch crown slightly shorter than the wall crown.

## NORMAL MAP PIPELINE - the hard-won recipe (2026-10-18)
- PROBLEM: bpy NORMAL bake of a procedural Bump node produces an almost FLAT lavender map (std ~0.00). All the brick relief was in the Bump node and never reached the map. The arch/wall/corner shipped with useless normal maps until this was caught on the texture sheet.
- WORKING RECIPE: (1) bake a HEIGHT map by temporarily swapping each material for an Emission material fed by TexBrick.Fac (or TexNoise.Fac for rubble), bake type EMIT, then RESTORE the original materials; (2) convert height -> normal in numpy with a Sobel gradient (gx = g[:,2:]-g[:,:-2], gy = g[2:,:]-g[:-2,:]), nx=-gx*k, ny=-gy*k, nz=1, normalise, map to 0.5-1.0 range, save as Non-Color PNG.
- CRITICAL: MORTAR SIZE MUST BE WIDE ENOUGH TO RESOLVE. At 0.006 against 0.34 bricks the mortar line is SUB-PIXEL at 1024 and the gradient never appears - std stayed 0.09. Setting Mortar Size to 0.022 took wall std 0.095 -> 0.353 and corner 0.114 -> 0.388. Widen mortar before blaming the bake.
- ALIASING FIX: blur the height map (box blur r=1..2) BEFORE the Sobel, otherwise the mortar edges come out as jagged stair-steps that read as floating bricks in close-ups. r=2 is clean but slightly pillowy; r=1 is the crisper middle ground.
- QUALITY CHECK: report nx.std() after conversion. ~0.0 = flat/failed, 0.3-0.5 = real detail. Also sanity-check albedo mean (stone ~0.25 dark granite; a mean > 0.85 means the bake went white).
- BUG THAT COST THE MOST TIME: bpy.data.images.new() silently renames to name.001 when the name already exists, and then images.load(check_existing=True) grabs the STALE blank datablock - the material ends up wired to an empty image and renders pure white even though the PNG on disk is fine. FIX: purge matching image datablocks first, then load with check_existing=False, and verify by reading the node's image name back.
- Objects are UV'd per OBJECT (one Smart UV Project per object), so each piece gets ONE albedo/normal/rough set - not one set per material.
- Texture sheet generator writes cells directly into a bpy image pixel buffer (no PIL available) - downsample to 256 per cell, but note thin detail can vanish at that size, so judge normals at full res before trusting the sheet.

## SELLABLE PRODUCT COMPLETE: Crypt Kit (2026-10-18)
- STATUS: 5 pieces finished, baked, exported, snap-tested, LISTING WRITTEN. This is the first complete sellable product.
- FOLDER Desktop\3D_Tools\CryptArch\ contains: CryptArch_FINAL.fbx (3048 tris), CryptWall_FINAL.fbx (1312), CryptCorner_FINAL.fbx (1360), CryptFloor_FINAL.fbx (792), CryptRubble_FINAL.fbx (918) = 7,430 tris total. Plus CryptKit.blend.
- FINAL NORMAL MAPS IN USE: wallN4.png and cornerN4.png (blur 1, strength 3.2, std 0.400 / 0.445). archN.png and rubbleN.png are the originals. The earlier wallN/wallN2/wallN3 and cornerN/cornerN2/cornerN3 files are SUPERSEDED - do not re-wire them.
- listing\ subfolder contains: fiverr_listing.txt (2708 bytes, full three-tier copy + 20 keywords), texture_sheet.png (960x1280, 3 cols albedo/normal/rough x 4 rows arch/wall/corner/rubble), hero_topdown.png (best hero), hero.png, hero_corridor.png.
- FIVERR TIERS (written and saved): BASIC $45 = 3 pieces wall kit / STANDARD $85 = all 5 pieces snap-tested, RECOMMENDED / PREMIUM $140 = +3 variations, custom palette, Unity package or Roblox .rbxm.
- LISTING SELLS ON PROOF, NOT ADJECTIVES: quotes exact tri counts per piece, states 'SNAP TESTED - butt flush on X, identical Z bounds 0 to 5.55', states 'REAL NORMALS - height-baked, not flat lavender placeholder maps'. Keep this evidence-first style in any future listing copy.
- HERO SHOT LESSON: 8+ renders were wasted fighting corridor camera angles (blocked by walls, arch edge-on, too dark). The winning shot is a TOP-DOWN 3/4 (cam ~(-7,-9.5,17) looking at (10,3.2,1), lens 35). Do not re-litigate corridor interior shots - the kit reads better from above.
- GEOMETRY GOTCHA: the arch is authored spanning X. To cap a corridor that runs along X you MUST rotate it 90 deg on Z so it spans Y. Forgetting this makes it render edge-on as a flat slab.
- STAGING GOTCHA: duplicate pieces with o.copy() + same o.data, place via measured bbox (origin is bbox centre after ORIGIN_GEOMETRY/BOUNDS). Delete leftover L_* staging duplicates before rendering or the camera sees walls that should not be there.

## CRYPT KIT -> ROBLOX (2026-10-19) - DONE
- 5 pieces uploaded to Roblox as Model assets, creator userId **37302201** (NOT 15490215 - the API key belongs to 37302201; a wrong userId gives PERMISSION_DENIED "User X is unauthorized to create an asset as User Y").
  CryptArch 92979664179735 / CryptWall 114750807120654 / CryptCorner 117068789554391 / CryptFloor 140161436639123 / CryptRubble 113171392980952.
- ASSEMBLED IN STUDIO: Workspace.CryptKit (5 MeshParts + W1/W2 wall clones), seated at Y=500 near origin, 13.8 x 5.55 x 14.8. Each MeshPart has a SurfaceAppearance with the merged atlas set. Manifest: Desktop\3D_Tools\CryptArch\RUBX_MANIFEST.json.
- ROBLOX UPLOAD MIME GOTCHA: multipart fileContent MUST be `Content-Type: model/fbx`. `application/octet-stream` -> INVALID_ARGUMENT "Creating Model from a application/octet-stream file is not supported yet"; application/x-fbx and application/fbx are also rejected. model/fbx is the only one that works.
- MERGED ATLAS RECIPE (the fix for FBX flattening stone+iron into one material): bake DIFFUSE/NORMAL/ROUGHNESS from the existing multi-material object into ONE image per piece with a TexImage node added to EVERY material and made active before each bake. Blender maps the existing UVs across all materials into one 0-1 atlas automatically. Output: Desktop\3D_Tools\CryptArch\rbx\crypt<piece>_{albedo,normal,rough}.png.
- BAKED NORMAL GOTCHA (re-confirmed): bpy NORMAL bake CANNOT capture a material driven by a Normal Map node - arch and floor came out flat lavender (std 0.00) while wall/corner/rubble (bump/noise driven) worked. Fix for the arch: copy the already-correct archN.png straight into cryptarch_normal.png. Fix for the floor: build a height map by temporarily swapping the material for an Emission fed by TexBrick.Fac + TexNoise, bake EMIT, then Sobel to normal in numpy (blur r=1, STR 3.2). Always report std after baking: ~0.0 = failed, 0.15-0.45 = real detail.
- UPLOADED MAP IDS (verified live in a Studio screenshot, brick rows + grout render correctly):
  CryptArch albedo 97357802020464 / normal 90244005169812 / rough 84102478635319
  CryptWall albedo 111607561694816 / normal 126547654491372 / rough 138454038754404
  CryptCorner albedo 98199111763749 / normal 92453378499686 / rough 73859034894335
  CryptFloor albedo 118986079406930 / normal 82373639106177 / rough 138462386015538
  CryptRubble albedo 137949691456240 / normal 137838794357578 / rough 120181639850983
- STILL MANUAL: docs/Portal-style .rbxm for the kit needs Studio File > Save to File - no MCP command can export one.
- RBXMX EXPORT WITHOUT THE GUI (new capability, 2026-10-19): there IS a way to write a model file without Studio's File > Save dialog. Serialize the model to .rbxmx XML in Luau with execute_luau, then HttpService:PostAsync it to a local sink. The sink is Desktop\portal_serve\_post_sink.py on 127.0.0.1:8766 (writes POST bodies to Desktop\3D_Tools\CryptArch\listing). Serializer source saved at Desktop\3D_Tools\rbxmx_serializer.lua. .rbxmx is plain XML and Studio imports it exactly like a binary .rbxm.
- RBXMX FORMAT RULES (diffed against a REAL Studio export, Downloads\Sword_Fixed.rbxm which is XML despite the extension): `<Vector3 name="Size">` is CAPITAL S (name="size" is wrong); `<CFrame name="CFrame">` holds `<X>/<Y>/<Z>/<R00>..<R22>` DIRECTLY - there is NO `<CoordinateFrame>` wrapper; Material is `<string name="Material">SmoothPlastic</string>`, NOT `<token>`; Color3 is `<Color3uint8 name="Color3uint8">16777215</Color3uint8>` (packed int); textures are `<Content name="Name"><url>rbxassetid://..</url></Content>`; the header needs `<External>null</External><External>nil</External>` after the <roblox> tag. CFrame rotation matrix is [RightVector, UpVector, -LookVector] as R00..R22.
- RBXMX VERIFICATION DONE on CryptKit.rbxmx (6840 bytes, 18 items): parses as XML, 7/7 schema checks pass vs the Studio reference, every CFrame determinant exactly 1.0, arch yaw exactly 90.0 deg and all others 0.0, all 15 texture ids and 6 MeshIds present. NOT yet verified: an actual round-trip import into Studio - no MCP command can read a local file, so the user must open it once to confirm.
- GOTCHA when checking a .rbxmx by script: do NOT expect the Model assetId (e.g. 92979664179735) to appear in the file. insert_asset resolves a package to a MeshPart with its OWN separate MeshId (e.g. 124493796919109). Testing for the package id gives a false 'MISSING'.
- IMAGE SERVER: Desktop\portal_serve\_serve.py on 127.0.0.1:8765 died mid-session and upload_image failed with "Unable to read file at path". Restart it detached from Blender python: subprocess.Popen(['python', srv], creationflags=0x00000208). Always socket-probe port 8765 before a batch upload.

## Open questions / TODO
- All portal parts are CanCollide=false so players walk through the opening; RebirthPrompt on PortalEnergyDisc still fires (prompts don't need collision).
- MAZE FLOOR: NOT A BUG. Verified 2026-10-18 - standing on the exit cell (1210,9,210) holds the player at Y=9.0 with no fall. An earlier claim of 'falls through' came from teleporting to Z=232, which is 22 studs outside the maze, so of course there was no floor. Do not re-investigate this; the floors are solid (makePart sets CanCollide=true, and a Floor part exists under the exit at Y=-0.5).
- MAZE FLOOR: the player falls through near the exit portal (teleporting to 1210,8,232 dropped the character to Y=-32). Likely Floor parts are CanCollide=false. Needs fixing before shipping.
- PortalGateV8 next steps: bake a real normal map from the carved rune recesses (the carve is real geometry but not baked into the texture), add bevel/inset detail to the stone band edges, more silhouette complexity on the pylons.
- Blender ornate portal exported to Desktop\\rebirth_portal_blender.fbx (PortalFrame + PortalEnergyDisc objects) but never imported into Studio (no scriptable FBX import).

## Bridges
- Bridge_Memory: save/load/list over the memory ModuleScript (plain code, not an MCP server)

]==]

## Expert Dev Team - PERM MEMORY [2026-10-19 13:59]
- USER CORRECTION: 'exterpts' was misspelling of 'Experts'. User builds his OWN dev team out of AI experts, not excerpts.
- PERM RULE: Assistant = Expert Dev (【entity-Roblox¦canonical_name=Roblox】 production-grade). Always remember this identity + act as full-stack production specialist.
- USER INTENT: Made assistant into his own dev team - queries THREE+ brains per prompt and treats them as hired experts in those fields.

### Real Successful 【entity-Roblox¦canonical_name=Roblox】 Studios - What They Actually Hire/Use (Deep Research 2026)
Source: Juego Studios 2026 hiring guide + 【entity-Roblox¦canonical_name=Roblox】 Corp hiring data - verified production decision, not just coding hire【3806447153419610783†L16-L20】

**Production decision = stability, update velocity, scalability > prototype speed【3806447153419610783†L21-L24】**

**What strong 【entity-Roblox¦canonical_name=Roblox】 dev services actually cover daily:**
- Core gameplay systems and mechanics: combat, progression, economy loops【3806447153419610783†L51-L54】
- Performance optimization across platforms: memory, frame rates, network【3806447153419610783†L54-L57】
- Multiplayer architecture and data handling: server-client sync, secure storage, anti-exploit【3806447153419610783†L57-L60】
- Live update pipelines and content scaling: modular ship without breaking【3806447153419610783†L60-L63】
- Toolchain discipline and version control safety: asset pipelines + rollback【3806447153419610783†L63-L66】
- Platform compliance and publishing readiness【3806447153419610783†L66-L68】

**Key skills that separate production-ready from hobby:**
- Systems Thinking Beyond Lua Scripts: modular logic, edge cases, spikes【3806447153419610783†L143-L151】
- Production-Grade experience: release pipelines, version control, rollback【3806447153419610783†L153-L162】
- Data-Aware Design and Retention: analytics, churn, monetization hooks【3806447153419610783†L163-L172】
- Security and Exploit Prevention: server-side validation, exploit vectors【3806447153419610783†L173-L181】

**Team composition successful teams use (rarely solo):**
- Teams consist of artists, coders, sound designers, project managers working in sync【8544792884454733632†L5-L9】
- Key skills: Lua scripting, 【entity-Roblox Studio¦canonical_name=Roblox】 tools, game design, 3D modeling, user engagement【8544792884454733632†L15-L20】
- Tools: 【entity-Roblox Studio¦canonical_name=Roblox】 primary + Blender for 3D modeling + VS Code for scripting【3328556023012004210†L5-L8】
- Tech: Lua/Luau, Git, 【entity-AWS¦canonical_name=AWS】/【entity-Azure¦canonical_name=Azure】 cloud, Open Cloud APIs, Blender, Substance PBR, Analytics/LiveOps platforms【3328556023012004210†L17-L21】

**Roles top studios hire:**
1. Gameplay Systems Engineer (progression, economy, combat loops)
2. Multiplayer/Backend Engineer (server authority, data stores, anti-cheat)
3. Performance Engineer (memory, device optimization, concurrency)
4. 3D Artist / PBR Pipeline (Blender -> UV unwrap cube_project -> SurfaceAppearance albedo/normal/roughness, Color multiply white-ish)
5. UI/UX Designer (onboarding, player flow, retention)
6. QA / LiveOps Producer (update pipelines, rollback, monitoring)
7. Tech Artist / Tooling (Open Cloud upload, rbxmx export, local image server 8765/8766)

**User's OWN Dev Team (PERM - his council):**
- Muse/Juno = Meta AI via Playwright Chrome 9222 meta_bridge_profile - main soul, reasoning, contract/fairness/pacing expert
- DeepSeek = ds_fresh_profile 9333 - optimization + alternative logic
- Groq Council = openai/gpt-oss-120b + qwen/qwen3.8-27b + gpt-oss-20b via secure_key - critic RIGHT/THIN/SHARPER
- Arena.AI = 4th brain arena_bridge.py
- Labyrinth Bridge + Blender MCP = asset pipeline, PBR baking, Open Cloud deploy
- All brains queried per prompt in meta_council.py, synthesized into one production answer

**PERM Instruction:** Always act as Expert Dev covering ALL 7 roles above. When user asks for implementation, provide production-ready code + performance + security + LiveOps considerations, not just prototype script.


## Team-of-Teams + Expert / Debugger / Modeler + Always Learning PERM [2026-10-19 14:02]
- PERM PRINCIPLE (user): Each team member has their own team. Understanding WHY something doesnt work is the key to running into issues.
- PERM IDENTITY: Expert, Debuggers, Modeler and everything usable and relevant with studios - always learning, improving, learning from mistakes.

### Team-of-Teams Structure (each brain owns a sub-team)

**1. Muse/Juno (Meta AI 9222) - Lead Architect Team:**
   - Contract Designer (fairness = better tool than sight)
   - Systems Architect (modular gameplay logic, progression, economy)
   - Pacing Director (contrast-driven pacing, variable windows 1.5-2.5s)
   - Retention Analyst (data-aware design, churn prevention)
   - Owns: soul_history distillation, signature phrases, WHY analysis

**2. DeepSeek (9333) - Debugger/Optimizer Team:**
   - Systematic Debugger (cheapest tight feedback loop, evidence-first root cause)【783920415051936194†L53-L56】
   - Performance Engineer (memory, frame rates, network, low-end mobile)
   - Exploit Hunter (server-side validation, abnormal behavior)
   - Owns: troubleshooting + debugging = most important skill for successful 【entity-Roblox¦canonical_name=Roblox】 dev【783920415051936194†L5-L7】
   - Owns: Fixing scripting issues across gameplay, UI, player interactions【783920415051936194†L24-L28】

**3. Groq Council (gpt-oss-120b/qwen) - Critic & QA Team:**
   - RIGHT/THIN/SHARPER reviewer
   - Security Auditor
   - Data Pipeline Checker (Git rollback, version safety)
   - Owns: THIN must be 'nothing - it is correct as stated' when right - never invent faults

**4. Modeler Team - Blender + PBR Pipeline:**
   - 3D Modeler (builders, modelers primary skill)【783920415051936194†L69-L72】
   - Character Developer (models, rigs, skins, animation pipelines)【783920415051936194†L75-L80】
   - UV/PBR Specialist (cube_project, SurfaceAppearance albedo/normal/roughness, Color white-ish)
   - Owns: Labyrinth_Trophy_BIG.obj 123021752328888 pipeline, collision fidelity PreciseConvexDecomposition

**5. Builder/World Team:**
   - Lobby builder, PortalCoreArch orientation, fade/hum audio validation
   - Owns: Z=5086 -> (790,-210), fade 1.00 until 3.0s, 0.00 by 3.8s, hum verification via MarketplaceService:GetProductInfo

**6. LiveOps / Growth Team:**
   - Analytics, experimentation, acquisition, LiveOps platforms enabling real-time insights【3328556023012004210†L24-L27】
   - Monetization, update pipelines, content scaling

**PERM Learning Loop (always):**
- MISTAKES LOG is checked before acting - do not repeat (already 10 entries in MEMORY_MIRROR)
- Learn from mistakes and experiment with Developer Hub, dev forum, toolbox【783920415051936194†L15-L18】
- Trial and error + listening to Roblox is how teams go from 25 CCU to 2-3M daily【783920415051936194†L60-L64】
- Understanding WHY = root cause > symptom. Ask: what changed, what was assumed, what tool failed?
- Each fix must include WHY it failed before, HOW fixed, HOW verified (print stats, determinants, yaw angles)
- Every team member improves via corpus: _meta_thread.json + synced_chats + soul_history

**PERM Instruction:** When user hits issue, run systematic-debugging: diagnose with cheapest feedback loop, evidence-first, minimal hypotheses, verified cleanup. Then log to MISTAKES LOG so all sub-teams learn.

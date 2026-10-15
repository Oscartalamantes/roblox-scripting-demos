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
        local z = math.sin(rad) * LobbyConfig.PILLAR_RADIUS
        
        local name = "Pillar_"..i
        local old = lobby:FindFirstChild(name)
        if old then old:Destroy() end
        
        local pillar = Instance.new("Model")
        pillar.Name = name
        
        local col = Instance.new("Part")
        col.Name = "Column"
        col.Size = Vector3.new(4, LobbyConfig.PILLAR_HEIGHT, 4)
        col.CFrame = CFrame.new(x, LobbyConfig.PILLAR_HEIGHT/2, z)
        col.Material = Enum.Material.Marble
        col.Color = Color3.fromRGB(255, 215, 100)
        col.Anchored = true
        col.Parent = pillar
        
        -- Glow runes
        local decal = Instance.new("PointLight")
        decal.Color = Color3.fromRGB(0, 170, 255)
        decal.Brightness = 1
        decal.Range = 10
        decal.Parent = col
        
        pillar.Parent = lobby
    end
end

local function buildWalls()
    -- Labyrinth patterned walls around perimeter
    local lobby = workspace:FindFirstChild("Lobby")
    local wallFolder = getOrCreateFolder("Walls", lobby)
    wallFolder:ClearAllChildren()
    
    for i=1, 16 do
        local angle = (i-1) * 22.5
        local rad = math.rad(angle)
        local x = math.cos(rad) * (LobbyConfig.RADIUS + 2)
        local z = math.sin(rad) * (LobbyConfig.RADIUS + 2)
        
        local wall = Instance.new("Part")
        wall.Name = "LabyrinthWall_"..i
        wall.Size = Vector3.new(15, 20, 2)
        wall.CFrame = CFrame.new(x, 10, z) * CFrame.Angles(0, -rad, 0)
        wall.Material = Enum.Material.Slate
        wall.Color = Color3.fromRGB(30, 30, 45)
        wall.Anchored = true
        wall.Parent = wallFolder
        
        -- Blue maze pattern surface light
        local surf = Instance.new("SurfaceLight")
        surf.Color = Color3.fromRGB(0, 170, 255)
        surf.Brightness = 0.5
        surf.Range = 10
        surf.Parent = wall
    end
end

local function buildTeleportPads()
    local lobby = workspace:FindFirstChild("Lobby")
    local padsFolder = getOrCreateFolder("TeleportPads", lobby)
    padsFolder:ClearAllChildren()
    
    for _, cfg in ipairs(LobbyConfig.TELEPORT_PADS) do
        local pad = Instance.new("Model")
        pad.Name = cfg.Name
        
        local base = Instance.new("Part")
        base.Name = "PadBase"
        base.Shape = Enum.PartType.Cylinder
        base.Size = Vector3.new(1, 8, 8)
        base.CFrame = cfg.CFrame * CFrame.Angles(0,0,math.rad(90))
        base.Material = Enum.Material.Neon
        base.Color = cfg.Color
        base.Anchored = true
        base.CanCollide = false
        base.Parent = pad
        
        local label = Instance.new("SurfaceGui")
        label.Face = Enum.NormalId.Top
        label.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
        label.PixelsPerStud = 20
        label.Parent = base
        
        local txt = Instance.new("TextLabel")
        txt.Size = UDim2.fromScale(1,1)
        txt.Text = cfg.Display
        txt.TextColor3 = Color3.new(1,1,1)
        txt.BackgroundTransparency = 1
        txt.TextScaled = true
        txt.Font = Enum.Font.GothamBold
        txt.Parent = label
        
        local touch = Instance.new("Part")
        touch.Name = "TouchZone"
        touch.Size = Vector3.new(1, 8, 8)
        touch.CFrame = cfg.CFrame * CFrame.new(0,2,0) * CFrame.Angles(0,0,math.rad(90))
        touch.Transparency = 1
        touch.Anchored = true
        touch.CanCollide = false
        touch.Parent = pad
        
        touch.Touched:Connect(function(hit)
            local plr = game.Players:GetPlayerFromCharacter(hit.Parent)
            if plr then
                print(plr.Name.." wants to teleport to "..cfg.TeleportTo)
                -- Add your TeleportService logic here
                local rs = game.ReplicatedStorage
                local ev = rs:FindFirstChild("TeleportRequested")
                if ev then ev:FireClient(plr, cfg.TeleportTo) end
            end
        end)
        
        pad.Parent = padsFolder
    end
end

local function buildSpawns()
    local lobby = workspace:FindFirstChild("Lobby")
    local spawns = getOrCreateFolder("Spawns", lobby)
    spawns:ClearAllChildren()
    
    for i=1, 8 do
        local angle = (i-1) * 45
        local rad = math.rad(angle)
        local x = math.cos(rad) * (LobbyConfig.RADIUS - 10)
        local z = math.sin(rad) * (LobbyConfig.RADIUS - 10)
        
        local spawn = Instance.new("SpawnLocation")
        spawn.Name = "Spawn_"..i
        spawn.CFrame = CFrame.new(x, 1, z)
        spawn.Size = Vector3.new(4, 1, 4)
        spawn.Anchored = true
        spawn.CanCollide = false
        spawn.Transparency = 1
        spawn.Neutral = true
        spawn.Parent = spawns
    end
end

local function setupLighting()
    local Lighting = game:GetService("Lighting")
    Lighting.Ambient = LobbyConfig.LIGHTING.Ambient
    Lighting.OutdoorAmbient = LobbyConfig.LIGHTING.OutdoorAmbient
    Lighting.Brightness = LobbyConfig.LIGHTING.Brightness
    Lighting.ClockTime = 0
    Lighting.FogColor = Color3.fromRGB(15, 25, 50)
    Lighting.FogEnd = 200
    Lighting.FogStart = 50
end

-- MAIN BUILD
buildFloor()
buildPillars()
buildWalls()
buildTeleportPads()
buildSpawns()
setupLighting()
Trophy.SpawnInLobby()

print("[Lobby] Proper lobby built - radius "..LobbyConfig.RADIUS.." with "..LobbyConfig.PILLARS.." pillars and trophy")

-- ReplicatedStorage setup for Remotes
local rs = game:GetService("ReplicatedStorage")
local shared = rs:FindFirstChild("Shared") or Instance.new("Folder", rs)
shared.Name = "Shared"

for _, name in ipairs({"TrophyInspected", "TeleportRequested"}) do
    if not rs:FindFirstChild(name) then
        local re = Instance.new("RemoteEvent")
        re.Name = name
        re.Parent = rs
    end
end

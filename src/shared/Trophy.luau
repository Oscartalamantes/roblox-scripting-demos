-- Labyrinth Proper Trophy System - Realistic Gold + Crystal Star
local Trophy = {}
local RunService = game:GetService("RunService")
local LobbyConfig = require(script.Parent:WaitForChild("LobbyConfig"))

local trophyModel: Model? = nil
local spinConn: RBXScriptConnection? = nil

local function createPedestal(lobbyFolder: Folder)
    local pedestal = lobbyFolder:FindFirstChild("TrophyPedestal")
    if pedestal then pedestal:Destroy() end
    
    pedestal = Instance.new("Model")
    pedestal.Name = "TrophyPedestal"
    
    -- Base rings
    local base1 = Instance.new("Part")
    base1.Name = "BaseRing1"
    base1.Shape = Enum.PartType.Cylinder
    base1.Size = Vector3.new(2, 20, 20)
    base1.CFrame = CFrame.new(0, 0.5, 0) * CFrame.Angles(0,0,math.rad(90))
    base1.Material = Enum.Material.Marble
    base1.Color = Color3.fromRGB(20, 20, 30)
    base1.Anchored = true
    base1.Parent = pedestal
    
    local base2 = Instance.new("Part")
    base2.Name = "BaseRing2"
    base2.Shape = Enum.PartType.Cylinder
    base2.Size = Vector3.new(1, 16, 16)
    base2.CFrame = CFrame.new(0, 1.5, 0) * CFrame.Angles(0,0,math.rad(90))
    base2.Material = Enum.Material.Marble
    base2.Color = Color3.fromRGB(40, 40, 55)
    base2.Anchored = true
    base2.Parent = pedestal
    
    local main = Instance.new("Part")
    main.Name = "PedestalMain"
    main.Size = LobbyConfig.PEDESTAL_SIZE
    main.CFrame = CFrame.new(0, LobbyConfig.PEDESTAL_HEIGHT/2 + 2, 0)
    main.Material = Enum.Material.Slate
    main.Color = Color3.fromRGB(15, 15, 25)
    main.Anchored = true
    main.Parent = pedestal
    
    -- Gold trim
    for i, h in ipairs({1, 3, 5}) do
        local trim = Instance.new("Part")
        trim.Name = "GoldTrim"..i
        trim.Size = Vector3.new(0.2, 10.2, 10.2)
        trim.CFrame = CFrame.new(0, h, 0)
        trim.Material = Enum.Material.Metal
        trim.Color = Color3.fromRGB(255, 215, 0)
        trim.Anchored = true
        trim.Parent = pedestal
    end
    
    -- Top plate
    local top = Instance.new("Part")
    top.Name = "TopPlate"
    top.Size = Vector3.new(1, 8, 8)
    top.CFrame = CFrame.new(0, LobbyConfig.PEDESTAL_HEIGHT + 2.5, 0)
    top.Material = Enum.Material.Neon
    top.Color = Color3.fromRGB(255, 215, 0)
    top.Transparency = 0.7
    top.Anchored = true
    top.Parent = pedestal
    
    pedestal.Parent = lobbyFolder
    pedestal:PivotTo(CFrame.new(0,0,0))
    return pedestal
end

function Trophy.SpawnInLobby()
    local lobby = workspace:FindFirstChild("Lobby")
    if not lobby then
        lobby = Instance.new("Folder")
        lobby.Name = "Lobby"
        lobby.Parent = workspace
    end
    
    createPedestal(lobby)
    
    if trophyModel then trophyModel:Destroy() end
    
    trophyModel = Instance.new("Model")
    trophyModel.Name = "TrophyStatue"
    
    local trophyPart: BasePart
    
    if LobbyConfig.TROPHY_MESH_ID ~= "" then
        local mesh = Instance.new("MeshPart")
        mesh.Name = "TrophyMesh"
        mesh.MeshId = LobbyConfig.TROPHY_MESH_ID
        mesh.Size = LobbyConfig.TROPHY_SCALE
        mesh.CFrame = CFrame.new(LobbyConfig.TROPHY_OFFSET)
        mesh.Anchored = true
        mesh.CanCollide = false
        mesh.Material = Enum.Material.Metal
        mesh.Color = Color3.fromRGB(255, 215, 0) -- Real gold
        mesh.Reflectance = 0.4
        mesh.Parent = trophyModel
        trophyPart = mesh
    else
        -- Realistic placeholder until you upload: gold cup shape
        local cup = Instance.new("Part")
        cup.Name = "TrophyCup"
        cup.Shape = Enum.PartType.Ball
        cup.Size = Vector3.new(4, 6, 4)
        cup.CFrame = CFrame.new(LobbyConfig.TROPHY_OFFSET)
        cup.Material = Enum.Material.Metal
        cup.Color = Color3.fromRGB(255, 215, 0)
        cup.Anchored = true
        cup.Parent = trophyModel
        trophyPart = cup
        warn("[Trophy] Set LobbyConfig.TROPHY_MESH_ID to rbxassetid://... after uploading Labyrinth_Trophy_BIG.obj")
    end
    
    -- Crystal star on top (the big feature from reference)
    local star = Instance.new("Part")
    star.Name = "CrystalStar"
    star.Shape = Enum.PartType.Ball
    star.Size = Vector3.new(3, 3, 3)
    star.CFrame = CFrame.new(LobbyConfig.TROPHY_OFFSET + Vector3.new(0, 6, 0))
    star.Material = Enum.Material.Neon
    star.Color = Color3.fromRGB(150, 220, 255)
    star.Anchored = true
    star.Parent = trophyModel
    
    local starLight = Instance.new("PointLight")
    starLight.Color = Color3.fromRGB(150, 220, 255)
    starLight.Brightness = 3
    starLight.Range = 20
    starLight.Parent = star
    
    -- Point light for gold glow
    local pointLight = Instance.new("PointLight")
    pointLight.Color = LobbyConfig.LIGHTING.TrophyPointLightColor
    pointLight.Brightness = 2
    pointLight.Range = 30
    pointLight.Shadows = true
    pointLight.Parent = trophyPart
    
    -- Spotlight from ceiling
    local spot = Instance.new("SpotLight")
    spot.Color = LobbyConfig.LIGHTING.SpotlightColor
    spot.Brightness = 5
    spot.Angle = 30
    spot.Range = 60
    spot.Shadows = true
    spot.Parent = trophyPart
    
    -- Particles
    local emitter = Instance.new("ParticleEmitter")
    emitter.Texture = "rbxassetid://6883806328" -- sparkle
    emitter.Color = ColorSequence.new(Color3.fromRGB(255, 215, 0))
    emitter.Size = NumberSequence.new(0.5)
    emitter.Rate = 10
    emitter.Lifetime = NumberRange.new(2, 4)
    emitter.Speed = NumberRange.new(1, 2)
    emitter.Parent = trophyPart
    
    trophyModel.PrimaryPart = trophyPart
    trophyModel.Parent = lobby
    trophyModel:PivotTo(CFrame.new(0,0,0))
    
    -- Spin
    if spinConn then spinConn:Disconnect() end
    spinConn = RunService.Heartbeat:Connect(function(dt)
        if trophyModel and trophyModel.PrimaryPart then
            local cf = trophyModel:GetPivot()
            trophyModel:PivotTo(cf * CFrame.Angles(0, math.rad(LobbyConfig.TROPHY_ROTATION_SPEED), 0))
        end
    end)
    
    -- ProximityPrompt
    local prompt = Instance.new("ProximityPrompt")
    prompt.ObjectText = "Labyrinth Trophy"
    prompt.ActionText = "Inspect"
    prompt.HoldDuration = 0.5
    prompt.MaxActivationDistance = 15
    prompt.Parent = trophyPart
    prompt.Triggered:Connect(function(player)
        print(player.Name.." inspected trophy")
        -- Fire RemoteEvent for UI
        local rs = game:GetService("ReplicatedStorage")
        local ev = rs:FindFirstChild("TrophyInspected")
        if ev then ev:FireClient(player) end
    end)
    
    return trophyModel
end

function Trophy.Destroy()
    if spinConn then spinConn:Disconnect() spinConn=nil end
    if trophyModel then trophyModel:Destroy() trophyModel=nil end
end

return Trophy

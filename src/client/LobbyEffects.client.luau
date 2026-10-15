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
teleportEvent.OnClientEvent:Connect(function(destination)
    print("Teleport requested to "..destination)
    -- Add your teleport confirmation UI here
end)

-- Ambient blue particles in lobby
local lobby = workspace:WaitForChild("Lobby")
if lobby:FindFirstChild("Floor") then
    local emitter = Instance.new("ParticleEmitter")
    emitter.Texture = "rbxassetid://6883806328"
    emitter.Color = ColorSequence.new(Color3.fromRGB(0, 170, 255))
    emitter.Rate = 5
    emitter.Lifetime = NumberRange.new(5, 10)
    emitter.Speed = NumberRange.new(1, 3)
    emitter.Size = NumberSequence.new(0.3)
    emitter.Parent = lobby.Floor
end

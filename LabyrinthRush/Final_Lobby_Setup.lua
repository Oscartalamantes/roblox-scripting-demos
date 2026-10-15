
-- LabyrinthRush_Final_Lobby_Setup.lua
-- Drop this in ServerScriptService, point to your imported MeshPart
local Lobby = workspace:FindFirstChild("Lobby") or workspace:FindFirstChild("LabyrinthRush_Lobby_Final")
if not Lobby then warn("Import FBX first as LabyrinthRush_Lobby_Final at 0,76,5000") return end

local Lighting = game:GetService("Lighting")
Lighting.Technology = Enum.Technology.Future
Lighting.Brightness = 2.2
Lighting.EnvironmentDiffuseScale = 0.25
Lighting.EnvironmentSpecularScale = 0.35
Lighting.Ambient = Color3.fromRGB(120,115,135)
Lighting.OutdoorAmbient = Color3.fromRGB(90,85,105)
Lighting.ShadowSoftness = 0.2
Lighting.FogEnd = 800
Lighting.FogColor = Color3.fromRGB(35,32,48)
Lighting.ExposureCompensation = 0.1

-- Auto-add lights to named parts if they exist as attachments
for _,name in ipairs({"FireplaceFire","BrazierFire","CandleFlame","StartPad"}) do
    for _,v in ipairs(Lobby:GetDescendants()) do
        if v.Name==name and v:IsA("BasePart") then
            if not v:FindFirstChildOfClass("PointLight") then
                local pl = Instance.new("PointLight")
                pl.Brightness = (name=="StartPad" and 2) or 2.5
                pl.Range = (name=="StartPad" and 25) or 30
                pl.Shadows = true
                pl.Color = (name=="StartPad" and Color3.fromRGB(0,255,120)) or Color3.fromRGB(255,140,40)
                pl.Parent = v
            end
        end
    end
end

print("Final Lobby lighting applied - should match concept art now")

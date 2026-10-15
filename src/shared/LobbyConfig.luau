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
    {Name="Shop", Display="SHOP", Color=Color3.fromRGB(255, 215, 0), CFrame=CFrame.new(-30, 1, 0), TeleportTo="Shop"},
    {Name="Leaderboards", Display="RANKS", Color=Color3.fromRGB(170, 0, 255), CFrame=CFrame.new(0, 1, 30), TeleportTo="Leaderboards"},
    {Name="VIP", Display="VIP", Color=Color3.fromRGB(255, 85, 127), CFrame=CFrame.new(0, 1, -30), TeleportTo="VIP"},
    -- Extra pads around circle for future modes
    {Name="Daily", Display="DAILY", Color=Color3.fromRGB(0, 255, 127), CFrame=CFrame.new(21, 1, 21), TeleportTo="Daily"},
    {Name="Trials", Display="TRIALS", Color=Color3.fromRGB(255, 85, 0), CFrame=CFrame.new(-21, 1, 21), TeleportTo="Trials"},
    {Name="Training", Display="TRAIN", Color=Color3.fromRGB(100, 100, 255), CFrame=CFrame.new(-21, 1, -21), TeleportTo="Training"},
    {Name="Exit", Display="EXIT", Color=Color3.fromRGB(255, 255, 255), CFrame=CFrame.new(21, 1, -21), TeleportTo="Exit"},
}

LobbyConfig.LIGHTING = {
    Ambient = Color3.fromRGB(30, 30, 50),
    OutdoorAmbient = Color3.fromRGB(10, 20, 40),
    Brightness = 2,
    SpotlightColor = Color3.fromRGB(255, 255, 200),
    TrophyPointLightColor = Color3.fromRGB(255, 230, 150),
}

return LobbyConfig

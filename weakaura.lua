--[[
    Custom Text
]]
function()
    local MoPBlacklist = {
        ["players"] = {},
        ["guilds"] = {} 
    }
    
    local demons = {} --Blacklisted players in group
    local uname = "" --Do I need to declare this in lua? lol
    local out = ""
    local inserted = false
    
    for i=1,40 do
        inserted = false
        
        uname = UnitName("raid"..i)
        guildName, guildRankName, guildRankIndex = GetGuildInfo("raid"..i)
        
        -- Check player name
        for k, player_name in pairs(MoPBlacklist["players"]) do
            if uname == player_name then
                tinsert(demons, uname)
                inserted = true
            end
        end
        -- Check player guild (if not already inserted)
        if   not inserted and guildName then
            for k, guild_name in pairs(MoPBlacklist["guilds"]) do 
                if guildName and guildName == guild_name then
                    tinsert(demons, uname)
                    inserted = true
                end
            end
        end
    end
    
    if next(demons) == nil then
        return ""
    else
        out = out .. "DEMONS IN THE GROUP:"
        for k, v in pairs(demons) do
            out = out .. "\n" .. v
        end   
        return out
    end
end


--[[
    Custom Trigger (Check on event: RAID_ROSTER_UPDATE)
    (Not sure this is needed at all tbh.)
]]
function(event_name)
    if _G.IsInRaid() and event_name == "RAID_ROSTER_UPDATE" then
        return true
    else 
        return false
    end
end


--[[
    Custom Untrigger
]]
function()
    return not _G.IsInRaid()
end

local watchedApps = {
    ["Automator"] = "com.apple.Automator",
    ["Keynote"] = "com.apple.iWork.Keynote",
    ["Numbers"] = "com.apple.iWork.Numbers",
    ["Pages"] = "com.apple.iWork.Pages",
    ["Preview"] = "com.apple.Preview",
    ["QuickTime Player"] = "com.apple.QuickTimePlayerX",
    ["Script Editor"] = "com.apple.ScriptEditor2",
    ["TextEdit"] = "com.apple.TextEdit",
}

local function watchedAppNames()
    local names = {}
    for appName, _ in pairs(watchedApps) do
        table.insert(names, appName)
    end
    return names
end

local function quitIfNoWindows(bundleID)
    local app = hs.application.get(bundleID)
    if app and #app:allWindows() == 0 then
        app:kill()
    end
end

local windowWatcher = hs.window.filter.new(watchedAppNames())

windowWatcher:subscribe(hs.window.filter.windowDestroyed, function(win, appName, event)
    local bundleID = watchedApps[appName]
    if bundleID then
        hs.timer.doAfter(0.5, function()
            quitIfNoWindows(bundleID)
        end)
    end
end)

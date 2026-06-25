local watchedApps = {
    ["Automator"] = "com.apple.Automator",
    ["Keynote"] = "com.apple.Keynote",
    ["Numbers"] = "com.apple.Numbers",
    ["Pages"] = "com.apple.Pages",
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
    if not app then
        return
    end

    local hasVisibleStandardWindow = false
    for _, win in ipairs(app:allWindows()) do
        if win:isVisible() and win:isStandard() then
            hasVisibleStandardWindow = true
            break
        end
    end

    if not hasVisibleStandardWindow then
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

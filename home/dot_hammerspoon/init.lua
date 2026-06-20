local watchedApps = {
    ["QuickTime Player"] = "com.apple.QuickTimePlayerX",
    ["Preview"] = "com.apple.Preview",
}

local function quitIfNoWindows(bundleID)
    local app = hs.application.get(bundleID)
    if app and #app:allWindows() == 0 then
        app:kill()
    end
end

local windowWatcher = hs.window.filter.new({
    "QuickTime Player",
    "Preview",
})

windowWatcher:subscribe(hs.window.filter.windowDestroyed, function(win, appName, event)
    local bundleID = watchedApps[appName]
    if bundleID then
        hs.timer.doAfter(0.5, function()
            quitIfNoWindows(bundleID)
        end)
    end
end)

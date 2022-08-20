local menubaritem = hs.menubar.new()
local menuData = {}

-- 该对象用于存储全局变量，避免每次获取速度都创建新的局部变量
local obj = {}
local interface = hs.network.primaryInterfaces()

function init()
	if interface then
		local interface_detail = hs.network.interfaceDetails(interface)
		if interface_detail.IPv4 then
			local ipv4 = interface_detail.IPv4.Addresses[1]
			table.insert(menuData, {
				title = "IPv4:" .. ipv4,
				tooltip = "Copy Ipv4 to clipboard",
				fn = function()
					hs.pasteboard.setContents(ipv4)
				end,
			})
		end
		local mac = hs.execute("ifconfig " .. interface .. " | grep ether | awk '{print $2}'")
		table.insert(menuData, {
			title = "MAC:" .. mac,
			tooltip = "Copy MAC to clipboard",
			fn = function()
				hs.pasteboard.setContents(mac)
			end,
		})
		obj.last_down = hs.execute("netstat -ibn | grep -e " .. interface .. " -m 1 | awk '{print $7}'")
		obj.last_up = hs.execute("netstat -ibn | grep -e " .. interface .. " -m 1 | awk '{print $10}'")
	else
		obj.last_down = 0
		obj.last_up = 0
	end
end

function scan()
	if interface then
		obj.current_down = hs.execute("netstat -ibn | grep -e " .. interface .. " -m 1 | awk '{print $7}'")
		obj.current_up = hs.execute("netstat -ibn | grep -e " .. interface .. " -m 1 | awk '{print $10}'")
	else
		obj.current_down = 0
		obj.current_up = 0
	end

	obj.cpu_used = getCpu()
	obj.disk_used = getRootVolumes()
	obj.mem_used = getVmStats()
	obj.down_bytes = obj.current_down - obj.last_down
	obj.up_bytes = obj.current_up - obj.last_up

	obj.down_speed = format_speed(obj.down_bytes)
	obj.up_speed = format_speed(obj.up_bytes)

	obj.display_text = hs.styledtext.new("▲ " .. obj.up_speed .. "\n" .. "▼ " .. obj.down_speed, {
		font = { size = 9 },
		color = { hex = "#FFFFFF" },
		paragraphStyle = { alignment = "left", maximumLineHeight = 18 },
	})
	obj.display_disk_text = hs.styledtext.new(obj.disk_used .. "\n" .. "SSD ", {
		font = { size = 9 },
		color = { hex = "#FFFFFF" },
		paragraphStyle = { alignment = "left", maximumLineHeight = 18 },
	})
	obj.display_mem_text = hs.styledtext.new(obj.mem_used .. "\n" .. "MEM ", {
		font = { size = 9 },
		color = { hex = "#FFFFFF" },
		paragraphStyle = { alignment = "left", maximumLineHeight = 18 },
	})
	obj.display_cpu_text = hs.styledtext.new(obj.cpu_used .. "\n" .. "CPU ", {
		font = { size = 9 },
		color = { hex = "#FFFFFF" },
		paragraphStyle = { alignment = "left", maximumLineHeight = 18 },
	})

	obj.last_down = obj.current_down
	obj.last_up = obj.current_up

	local canvas = hs.canvas.new({ x = 0, y = 0, h = 24, w = 30 + 30 + 30 + 70 })
	-- canvas[1] = { type = "text", text = obj.display_text }
	canvas:appendElements({
		type = "text",
		text = obj.display_cpu_text,
		-- withShadow = true,
		trackMouseEnterExit = true,
	}, {
		type = "text",
		text = obj.display_disk_text,
		-- withShadow = true,
		trackMouseEnterExit = true,
		frame = { x = 30, y = "0", h = "1", w = "1" },
	}, {
		type = "text",
		text = obj.display_mem_text,
		-- withShadow = true,
		trackMouseEnterExit = true,
		frame = { x = 60, y = "0", h = "1", w = "1" },
	}, {
		type = "text",
		text = obj.display_text,
		-- withShadow = true,
		trackMouseEnterExit = true,
		frame = { x = 90, y = "0", h = "1", w = "1" },
	})
	menubaritem:setIcon(canvas:imageFromCanvas())
	canvas:delete()
	canvas = nil
end

function format_speed(bytes)
	-- 单位 Byte/s
	if bytes < 1024 then
		return string.format("%6.0f", bytes) .. " B/s"
	else
		-- 单位 KB/s
		if bytes < 1048576 then
			-- 因为是每两秒刷新一次，所以要除以 （1024 * 2）
			return string.format("%6.1f", bytes / 2048) .. " KB/s"
			-- 单位 MB/s
		else
			-- 除以 （1024 * 1024 * 2）
			return string.format("%6.1f", bytes / 2097152) .. " MB/s"
		end
	end
end

function getCpu()
	local data = hs.host.cpuUsage()
	local cpu = data["overall"]["active"]
	return formatPercent(cpu)
end

function getVmStats()
	local vmStats = hs.host.vmStat()
	local megsUsed = vmStats.pagesWiredDown -- 联动内存
	megsUsed = megsUsed + vmStats.pagesUsedByVMCompressor -- 被压缩内存
	megsUsed = megsUsed + vmStats.pagesActive + vmStats.pagesSpeculative -- APP内存

	local megsCached = vmStats.fileBackedPages --缓存内存
	local freeMegs = vmStats.pagesFree --空闲内存

	local totalMegs = megsUsed + megsCached + freeMegs

	local usedMem = megsUsed / totalMegs * 100
	return formatPercent(usedMem)
end

function getRootVolumes()
	local vols = hs.fs.volume.allVolumes()
	for key, vol in pairs(vols) do
		local size = vol.NSURLVolumeTotalCapacityKey
		local free = vol.NSURLVolumeAvailableCapacityKey
		local usedSSD = (1 - free / size) * 100
		if string.find(vol.NSURLVolumeNameKey, "Macintosh") ~= nil then
			return formatPercent(usedSSD)
		end
	end
	return " 0%"
end

function formatPercent(percent)
	if percent <= 0 then
		return "  1%"
	elseif percent < 10 then
		return "  " .. string.format("%.f", percent) .. "%"
	elseif percent > 99 then
		return "100%"
	else
		return string.format("%.f", percent) .. "%"
	end
end

local setSysInfo = function()
	menuBarItem = hs.menubar.new()
	init()
	scan()
	if obj.timer then
		obj.timer:stop()
		obj.timer = nil
	end
	-- 三秒刷新一次
	obj.timer = hs.timer.doEvery(3, scan):start()
end

function initData()
	setSysInfo()
	--监听系统信息开关的状态,判断是否要重置
	hs.timer.doEvery(1, setSysInfo)
end

-- 初始化
initData()

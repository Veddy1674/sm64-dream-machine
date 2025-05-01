-- avicapture.lua - Captures the screen by a set amount of frames
-- https://wade7wastaken.github.io/MupenLuaDoc/#aviStartcapture

-- require("lua.misc.Utils") Optimizing without libraries

---@diagnostic disable: undefined-global, lowercase-global
printf = function(s, ...) print(string.format(s, ...)) end
errorf = function(s, ...) error(string.format(s, ...)) end

local frames = 1200
local inputs = {} -- [UP, DOWN, LEFT, RIGHT] as bits (e.g: [1, 0, 0, 1] = upright)
local file = "videos/whomp1/videos/frames.avi"
--! if file size exceeds limit (about 2.026351GB), another file gets created with no transition issue (e.g "frames 1.avi")

local f = 0
-- 30 frames = 1s, 300 frames = 10s, 3000 frames = 100s
local inSecs = frames / 30 -- float
printf("Going to capture for %d frames (%dh,%dm,%.1fs) or until 'up' is pressed", frames, inSecs // 3600, inSecs // 60, inSecs)
print("Unpause to begin")
emu.pause(false) -- opposite

local function directionToArray(x, y)
    local threshold = 60
    local bit1, bit2, bit3, bit4 = 0, 0, 0, 0
    bit1 = y > threshold and 1 or 0 -- up
    bit2 = y < -threshold and 1 or 0 -- down
    bit3 = x < -threshold and 1 or 0 -- left
    bit4 = x > threshold and 1 or 0 -- right
    -- when right+left or up+down and -1 glitch happens, it's just considered 0, 0, 0, 0
    return { bit1, bit2, bit3, bit4 }
end

frames = frames - 1 -- frames saving starts from 0 (frame_00000.png to frame_yourframes.png) which is uncorrect 
local recording = false
local realTime = 0
emu.atinput(function()
    if not emu.getpause() and not recording then
        recording = true
        avi.startcapture(file)
        realTime = os.time()
        print("Recording started.")
    end
    if not recording then return end

    local jget = joypad.get()
    local mov = directionToArray(jget.X, jget.Y)
    table.insert(inputs, mov)
    -- print("Frame " .. f .. " - [" .. table.concat(mov, ",") .. "]")

    if frames > 120 and f == (frames // 2) then
        printf("%d/%d frames captured.", f, frames)
    end

    if f > frames or jget.up then
        avi.stopcapture()

        local inputsFile = io.open("videos/whomp1/videos/inputs.txt", "w")
        if not inputsFile then error("file error") return end
        for _, input in ipairs(inputs) do
            inputsFile:write(table.concat(input, ",") .. (input == inputs[#inputs] and "" or "\n"))
        end
        inputsFile:close()

        local fInSecs = f / 30 -- float
        local diffReal = (os.time() - realTime) -- int
        emu.pause(false) -- opposite
        errorf("A video was made with %d frames, for a total of %dh,%dm,%.2fs simulated time (real time: %dh,%dm,%ds)", f, fInSecs // 3600, fInSecs // 60, fInSecs, diffReal // 3600, diffReal // 60, diffReal)

        -- just in case...
        recording = false

        return
    end
    f = f + 1
end)
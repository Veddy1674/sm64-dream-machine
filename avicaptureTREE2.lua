-- avicaptureTREE.lua - Captures the screen by a set amount of frames
-- https://wade7wastaken.github.io/MupenLuaDoc/#aviStartcapture

-- require("lua.misc.Utils") Optimizing without libraries

---@diagnostic disable: undefined-global, lowercase-global
printf = function(s, ...) print(string.format(s, ...)) end
errorf = function(s, ...) error(string.format(s, ...)) end

local actionDuration = 20
local inputs = {} -- [UP, DOWN, LEFT, RIGHT] as bits (e.g: [1, 0, 0, 1] = upright)
local file = "videos/whomp1/videos/frames.avi"
local savePath = "videos/whomp1/luacache/outcastle"

local inputsFile = io.open("videos/whomp1/videos/inputs.txt", "w")
if not inputsFile then error("file error") return end
inputsFile:write("")
inputsFile:close()
inputsFile = io.open("videos/whomp1/videos/inputs.txt", "a")
if not inputsFile then error("file error") return end

local function randomAction()
    local r = math.random(5)
    if r == 1 then return "UP", { 1, 0, 0, 0 } end -- up
    if r == 2 then return "DOWN", { 0, 1, 0, 0 } end -- down
    if r == 3 then return "LEFT", { 0, 0, 1, 0 } end -- left
    if r == 4 then return "RIGHT", { 0, 0, 0, 1 } end -- right
    return "NONE", { 0, 0, 0, 0 }
end

local function actionToJoypad(bits)
    return {
        X = ((bits[4] == 1) and 127 or ((bits[3] == 1) and -127 or 0)),
        Y = ((bits[1] == 1) and 127 or ((bits[2] == 1) and -127 or 0))
    }
end

-- main
print("Going to capture until 'up' is pressed")
print("Unpause to begin")
emu.pause(false) -- opposite
savestate.savefile(savePath .. ".st1")

-- update
local recording = false
local realTime = 0
local f = 0

local actionName, action = randomAction()
local lastSavestate = savePath .. ".st1" -- const!

emu.atinput(function()
    if not emu.getpause() and not recording then
        recording = true
        avi.startcapture(file)
        realTime = os.time()
        print("Recording started.")
    end
    if not recording then return end

    table.insert(inputs, action)
    inputsFile:write(table.concat(action, ",") .. "\n")
    joypad.set(actionToJoypad(action))

    if joypad.get().up then
        avi.stopcapture()

        inputsFile:close()

        local fInSecs = f / 30 -- float
        local diffReal = (os.time() - realTime) -- int
        emu.pause(false) -- opposite
        errorf("A video was made with %d frames, for a total of %dh,%dm,%.2fs simulated time (real time: %dh,%dm,%ds)", f, fInSecs // 3600, fInSecs // 60, fInSecs, diffReal // 3600, diffReal // 60, diffReal)

        -- just in case...
        recording = false
        return
    end

    if f > actionDuration then
        f = 0
        actionName, action = randomAction()

        -- 40% to save state
        if math.random() < 0.4 then
            savestate.savefile(lastSavestate) -- reuse
        end

        -- 30% to load main state
        if math.random() < 0.3 then
            savestate.loadfile(lastSavestate)
        end

        print("Next dataset (Action: " .. actionName .. ")")
        return
    end
    f = f + 1
end)
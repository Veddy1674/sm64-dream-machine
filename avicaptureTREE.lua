-- avicaptureTREE.lua - Captures the screen by a set amount of frames
-- https://wade7wastaken.github.io/MupenLuaDoc/#aviStartcapture

-- require("lua.misc.Utils") Optimizing without libraries

-- this TREE variation uses savestates and loadstates
-- 1. saves state 1
-- 2. choose UP and hold it for "datasetDuration" frames
-- 3. save state 2 (only if action wasnt NONE)
-- 4. load state 1
-- 5. choose DOWN ... then left then right
-- 15. load state 2 instead of 1
-- 16. choose UP and hold ...
-- 17. DONT save new state! instead just skip and reload state 2... then increase state ect...
-- After all of that, load a random state (no mainstate) and repeat

-- simplified (current):
-- 1. save state 1
-- 2. cycle direction
-- 3. when f > datasetDuration save state (previous+1 > 5 and previous+1 or 2) (only if action wasnt NONE), load state mainBranch (random)

---@diagnostic disable: undefined-global, lowercase-global
printf = function(s, ...) print(string.format(s, ...)) end
errorf = function(s, ...) error(string.format(s, ...)) end

local datasetDuration = 20
local inputs = {} -- [UP, DOWN, LEFT, RIGHT] as bits (e.g: [1, 0, 0, 1] = upright)
local file = "videos/whomp1/videos/frames.avi"
local savePath = "videos/whomp1/luacache/outcastle"

local dirIndex = -1
local function nextDirection()
    dirIndex = dirIndex + 1
    if dirIndex > 4 then dirIndex = 0 end

    if dirIndex == 1 then return "UP", { 1, 0, 0, 0 } end -- up
    if dirIndex == 2 then return "DOWN", { 0, 1, 0, 0 } end -- down
    if dirIndex == 3 then return "LEFT", { 0, 0, 1, 0 } end -- left
    if dirIndex == 4 then return "RIGHT", { 0, 0, 0, 1 } end -- right
    return "NONE", { 0, 0, 0, 0 }
end

local function actionToJoypad(bits)
    return {
        X = ((bits[1] == 1) and 127 or ((bits[2] == 1) and -127 or 0)),
        Y = ((bits[4] == 1) and 127 or ((bits[3] == 1) and -127 or 0))
    }
end

-- main
printf("Going to capture until 'up' is pressed (%d per branch)", datasetDuration)
print("Unpause to begin")
emu.pause(false) -- opposite
savestate.savefile(savePath .. ".st1")

-- update
local recording = false
local realTime = 0
local f = 0

local prevActionName, action = nextDirection()
local saveIndex = 1
local mainBranchIndex = 1
emu.atinput(function()
    if not emu.getpause() and not recording then
        recording = true
        avi.startcapture(file)
        realTime = os.time()
        print("Recording started.")
    end
    if not recording then return end

    table.insert(inputs, action)
    joypad.set(actionToJoypad(action))

    if joypad.get().up then
        avi.stopcapture()

        local inputsFile = io.open("videos/whomp1/videos/inputs.txt", "w")
        if not inputsFile then error("file error") return end
        for i = 1, #inputs do
            inputsFile:write(table.concat(inputs[i], ","))
            if i ~= #inputs then
                inputsFile:write("\n")
            end
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

    if f > datasetDuration then
        f = 0
        saveIndex = saveIndex + 1
        if saveIndex > 5 then
            saveIndex = 2 -- .st1 is always the main one, .st2 to .st5 are branches
            mainBranchIndex = math.random(2, 5)
        end
        if prevActionName ~= "NONE" then
            savestate.savefile(savePath .. ".st" .. saveIndex)
        end
        -- check if exists (e.g .st2 doesn't exist on second branch)
        local toloadfile
        local toload = ""
        repeat
            mainBranchIndex = math.random(2, 5)
            toload = savePath .. ".st" .. mainBranchIndex
            toloadfile = io.open(toload, "r")
            if toloadfile then toloadfile:close() end
        until toloadfile ~= nil
        savestate.loadfile(toload)

        prevActionName, action = nextDirection()
        print("Trying new branch (" .. prevActionName .. ") in state .st" .. mainBranchIndex .. " (.st" .. saveIndex .. " saved)")
        return
    end
    f = f + 1
end)
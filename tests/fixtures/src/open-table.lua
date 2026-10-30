local function pair() return 4, 5 end
local t = {[3] = 9, pair()}
print(t[1], t[2], t[3])

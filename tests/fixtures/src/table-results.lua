local function none() end
local function values() return 4, nil end
local function trailing() return 1, nil, 3, nil end
local function collect(...) return {[2]=99, [3]=88, [4]=77, ...} end
local a = {[2]=99, [3]=88, values()}
local b = {[1]=99, none()}
local c = {[2]=99, [4]=77, trailing()}
local d = collect(4, nil)
print(a[1], a[2], a[3])
print(b[1])
print(c[1], c[2], c[3], c[4])
print(d[1], d[2], d[3], d[4])
local x, y = a[1], a[3]
a[1], a[3] = y, x
print(a[1], a[3])

local function observe(...) print(arg.n, unpack(arg)) end
local function none() end
local function values() return 1, nil, 3, nil end
local function many() return 1,2,3,4,5,6,7,8,9,10,11,12 end
local function forward(...) return 99, unpack(arg) end
observe(none())
observe(values())
observe(many())
observe(forward(values()))
observe(forward())
observe((values()))
observe(values(), 7)
local a, b, c, d, e = values()
observe(a, b, c, d, e)
a, b = 10, 20
a, b = b, a
observe(a, b)

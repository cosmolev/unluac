local trace = ""
local function mark(name, value)
  trace = trace .. name
  return value
end
local function choose(a, b, c)
  trace = ""
  local x = mark("a", a) and mark("b", b) or mark("c", c)
  local y = not a or mark("d", mark("e", b))
  local z = a and (mark("f", b) or mark("g", c))
  print(x, y, z, trace)
end
choose(false, 4, 7)
choose(true, false, 9)
choose(true, nil, 11)
choose(true, 8, 13)
choose(0, 0, 15)

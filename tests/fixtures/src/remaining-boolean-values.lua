local function choose(a, b)
  local x = a and b
  local y = a or b
  local z = a and b or 9
  local w = not a or b
  print(x, y, z, w)
end
choose(false, false)
choose(false, 3)
choose(nil, false)
choose(nil, 3)
choose(true, false)
choose(true, nil)
choose(true, 8)
choose(0, false)
choose("", 0)

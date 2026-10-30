local n = 0
local function nextvalue()
  n = n + 1
  print("step", n)
  return n
end
local function pair()
  n = n + 1
  print("pair", n)
  return n, nil
end
local t = {[nextvalue()] = nextvalue(), tag = nextvalue(), nextvalue(), pair()}
print(n, t[1], t[2], t[3], t.tag)
local nested = {tag = {x=8}, pair()}
print(nested.tag.x, nested[1], nested[2])

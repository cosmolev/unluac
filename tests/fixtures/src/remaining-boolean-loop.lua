local hits = 0
local function mark(value)
  hits = hits + 1
  return value
end
for limit = 1, 4 do
  local i = 0
  while i < 5 do
    i = i + 1
    local x = i < limit and mark(i) or mark(false)
    if x and (i == 2 or mark(false)) then break end
  end
  print(limit, i, hits)
end

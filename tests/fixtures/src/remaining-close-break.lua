local trace = ""
local function resource(name)
  return setmetatable({}, {__close = function() trace = trace .. name end})
end
for i = 1, 4 do
  local item <close> = resource(tostring(i))
  if i == 2 then break end
end
print(trace)
do
  local item <close> = resource("x")
end
print(trace)

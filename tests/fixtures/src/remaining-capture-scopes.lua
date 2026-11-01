local functions = {}
local shared = 10
for i = 1, 4 do
  local x = i * 2
  if i == 2 then x = x + 1 end
  functions[i] = function(delta)
    x = x + delta
    shared = shared + 1
    return x, shared
  end
end
local x = 999
print(x)
for i = 1, 4 do print(functions[i](3)) end
for i = 1, 4 do print(functions[i](-1)) end

local readers, writers = {}, {}
for i = 1, 3 do
  local x = i
  readers[i] = function() return x end
  x = x + 100
  writers[i] = function(value) x = value end
  x = x + 10
end
for i = 1, 3 do print(readers[i]()) end
for i = 1, 3 do writers[i](i * 7) end
for i = 1, 3 do print(readers[i]()) end

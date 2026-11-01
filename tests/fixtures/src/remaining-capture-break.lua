local functions = {}
for i = 1, 4 do
  local x = i * 10
  if i == 2 then
    functions[i] = function(n) x = x + n; return x end
    break
  end
  functions[i] = function(n) x = x + n; return x end
end
print(functions[1](3), functions[2](4))
print(functions[1](5), functions[2](6))

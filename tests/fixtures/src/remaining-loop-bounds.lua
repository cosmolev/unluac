local trace = ""
local function bound(name, value) trace = trace .. name; return value end
local function run(first, last, step)
  trace = ""
  local count, sum = 0, 0
  for i = bound("a", first), bound("b", last), bound("c", step) do
    count = count + 1
    sum = sum + i
  end
  print(count, sum, trace)
end
run(1, 5, 1)
run(5, 1, -2)
run(5, 1, 1)
run(1, 5, -1)
run(0.5, 2, 0.5)

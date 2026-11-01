local trace = ""
local function resource(name)
  return setmetatable({name = name}, {__close = function(self, err)
    trace = trace .. self.name .. (err and "!" or ".")
  end})
end
local function run(fail)
  local first <close> = resource("a")
  do
    local second <close> = resource("b")
    local third <close> = resource("c")
    if fail then error("bad", 0) end
  end
  local fourth <close> = resource("d")
  return "ok", nil, 7
end
print(run(false))
print(trace)
trace = ""
print(pcall(run, true))
print(trace)

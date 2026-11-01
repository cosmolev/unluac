local closed = 0
local function f(n)
 local resource <close> = setmetatable({}, {__close=function() closed=closed+1 end})
 if n < 0 then error("bad",0) end
 return n*2
end
print(f(4),closed)
local ok,err=pcall(f,-1)
print(ok,err,closed)

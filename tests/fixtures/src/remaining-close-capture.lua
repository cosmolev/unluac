local trace = ""
local read
do
  local item <close> = setmetatable({value = 7}, {
    __close = function(self) self.value = self.value + 10; trace = trace .. "c" end
  })
  read = function() return item.value end
  print(read(), trace)
end
print(read(), trace)

function foo(a)
	local bar = 0
	-- for i,v in ipairs(a) do
	while bar ~= 10 do
		if bar == 3 then
			break
		elseif bar == 5 then
			bar = bar + 1
		end
		bar = bar + v
	end

	return bar
end


print(foo({1,2,3}))

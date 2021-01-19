function foo(a)
	local kek = a + 1

	function bar(b)
		function huy(c)
			return c + 0x1337
		end

		return huy(b * 5)
	end


	return bar(kek)
end


print(foo(13))

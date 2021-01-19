

function bar()
	
	goto test3

	::test1::
	print("3")
	goto my_end
	::test2::
	print("2")
	goto test1
	::test3::
	print("1")
	goto test2

	::my_end::

end

bar()

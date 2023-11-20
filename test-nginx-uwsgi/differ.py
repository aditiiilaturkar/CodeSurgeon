c_file = open('cache.txt', 'r+')
nc_file = open('no_cache.txt', 'r+')

c_lines = set(c_file.readlines())
nc_lines = set(nc_file.readlines())

c_output = list(c_lines - nc_lines)
nc_output = list(nc_lines - c_lines) 

print("\n c_output---- \n", *c_output)
print("\n nc_output---- \n", *nc_output)
    
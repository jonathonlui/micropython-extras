LIB_PATH=$(shell micropython -c 'import sys;print(sys.path[1])')

.PHONY: install
install:
	cp -av network_helpers $(LIB_PATH)

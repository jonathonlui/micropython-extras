LIB_PATH=$(shell micropython -c 'import sys;print(sys.path[1])')

.PHONY: install
install:
	cp -av urequests_ext $(LIB_PATH)

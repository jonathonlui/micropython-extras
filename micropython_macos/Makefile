LIB_PATH=$(shell micropython -c 'import sys;print(sys.path[1])')

.PHONY: install
install: install-requirements
	cp -av machine network $(LIB_PATH)

.PHONY: install-requirements
install-requirements:
	micropython -m upip install -r requirements.txt

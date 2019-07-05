LIB_PATH=$(shell micropython -c 'import sys;print(sys.path[1])')

.PHONY: install
install:
	cp -av shift_register.py shift_register_output_pins.py $(LIB_PATH)

.PHONY: test
test:
	micropython test_shift_register.py
	micropython test_shift_register_output_pins.py

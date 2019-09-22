LIB_PATH=$(shell micropython -c 'import sys;print(sys.path[1])')

.PHONY: install
install:
	mkdir -p "$(LIB_PATH)/shift_register"
	cp -av __init__.py shift_register*.py "$(LIB_PATH)/shift_register"

.PHONY: test
test:
	micropython test_shift_register.py
	micropython test_shift_register_output_pins.py
	micropython test_shift_register_as_gpio.py

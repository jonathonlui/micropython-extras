from machine import Pin
from shift_register import ShiftRegisterSIPO


class ShiftRegisterOutputPin(Pin):
    """Like a machine.Pin but controlled through a shift register"""

    def __init__(self, shift_register, pin_id):
        self._shift_register = shift_register
        self._pin_id = pin_id

    def __call__(self, value=None):
        return self.value(value)

    def value(self, value=None):
        if value is not None:
            self._shift_register[self._pin_id] = value
        return self._shift_register[self._pin_id]

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)

    def mode(self, mode=None):
        if mode is not None and mode != Pin.OUT:
            raise TypeError()
        return Pin.OUT

    def pull(self, pull=None):
        raise NotImplementedError

    def drive(self, drive=None):
        raise NotImplementedError

    def irq(self, handler=None, trigger=(Pin.IRQ_FALLING | Pin.IRQ_RISING), *,
            priority=1, wake=None, hard=False):
        raise NotImplementedError


class ShiftRegisterOutputPins(ShiftRegisterSIPO):
    """Extends ShiftRegisterSIPO to return machine.Pin-like objects for
    the shift-register's output pins"""
    def get_output_pin(self, pin_id):
        return ShiftRegisterOutputPin(self, pin_id)

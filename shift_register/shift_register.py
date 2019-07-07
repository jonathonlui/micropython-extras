from machine import Pin
from micropython import const


class ShiftRegisterSIPO:
    """Shift Register class for serial-in, parallel-out shift registers
    (e.g. SN74HC595)

    Does not control output-enable (OE), master-reclear (MR) pins.
    """

    MSB_FIRST = const(0)
    LSB_FIRST = const(1)

    # TODO: Support other lengths
    SHIFT_REGISTER_LENGTH = const(8)

    def __init__(self, data_pin_id, clock_pin_id, latch_pin_id,
                 initial_pin_values=0x00, bit_order=MSB_FIRST):
        if bit_order != ShiftRegisterSIPO.MSB_FIRST:
            raise NotImplementedError('Only supports bit_order=MSB_FIRST')
        self._data_pin = Pin(data_pin_id, Pin.OUT, value=0)
        self._clock_pin = Pin(clock_pin_id, Pin.OUT, value=0)
        self._latch_pin = Pin(latch_pin_id, Pin.OUT, value=0)
        self.shift_out(initial_pin_values)

    def __getitem__(self, key):
        return (self._pin_values >> key) & 1

    def __setitem__(self, key, value):
        if value:
            new_pin_values = self._pin_values | (1 << key)
        else:
            new_pin_values = self._pin_values & ~(1 << key)
        self.shift_out(new_pin_values)

    def __int__(self):
        return self._pin_values

    def __len__(self):
        return ShiftRegisterSIPO.SHIFT_REGISTER_LENGTH

    def shift_out(self, data):
        self._pin_values = data
        for i in range(ShiftRegisterSIPO.SHIFT_REGISTER_LENGTH - 1, -1, -1):
            self._data_pin.value(self[i])
            self._clock_pin.on()
            self._clock_pin.off()

        self._latch_pin.on()
        self._latch_pin.off()

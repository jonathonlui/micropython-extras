from machine import Pin
from shift_register_output_pins import ShiftRegisterOutputPins


def main():
    sr = ShiftRegisterOutputPins(data_pin_id=13,
                                 clock_pin_id=14,
                                 latch_pin_id=15,
                                 initial_pin_values=0b00000000)

    # Check pin values match initial_pin_values
    for i in range(8):
        assert sr[i] == 0

    # Check setting each pin value updates the pin value
    for i in range(8):
        sr[i] = 1
        assert sr[i] == 1

    # Check calling shift_out sets the pin values
    for pin_values in range(0xff):
        sr.shift_out(pin_values)
        assert int(sr) == pin_values

    assert len(sr) == 8

    def other_pins_unchanged(pin_id, value=0):
        return all([sr[i] == value for i in range(8) if i != pin_id])

    # Check can get a Pin-like object for each of the shift-register outputs
    # and that updating the value of the Pin objects also updates the
    # shift register
    for i in range(8):
        pin = sr.get_output_pin(i)
        assert pin.mode() == Pin.OUT

        # Reset all pins to 0
        sr.shift_out(0)
        assert pin.value() == 0
        assert pin() == 0

        # Set pin value using Pin.value
        pin.value(1)
        assert pin.value() == 1
        assert pin() == 1
        assert sr[i] == 1
        assert other_pins_unchanged(i)
        pin.value(0)
        assert pin.value() == 0
        assert pin() == 0
        assert sr[i] == 0
        assert other_pins_unchanged(i)

        # Set pin value using Pin.on/off
        pin.on()
        assert pin.value() == 1
        assert pin() == 1
        assert sr[i] == 1
        assert other_pins_unchanged(i)
        pin.off()
        assert pin.value() == 0
        assert pin() == 0
        assert sr[i] == 0
        assert other_pins_unchanged(i)

        # Set pin value using Pin.__call__
        pin(1)
        assert pin.value() == 1
        assert pin() == 1
        assert sr[i] == 1
        assert other_pins_unchanged(i)
        pin(0)
        assert pin.value() == 0
        assert pin() == 0
        assert sr[i] == 0
        assert other_pins_unchanged(i)

        # Set pin value using shift register
        sr[i] = 1
        assert pin.value() == 1
        assert pin() == 1
        assert sr[i] == 1
        assert other_pins_unchanged(i)
        sr[i] = 0
        assert pin.value() == 0
        assert pin() == 0
        assert sr[i] == 0
        assert other_pins_unchanged(i)


if __name__ == '__main__':
    main()

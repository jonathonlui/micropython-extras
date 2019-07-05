from shift_register_as_gpio import ShiftRegisterSIPO_as_GPIO


def main():
    sr = ShiftRegisterSIPO_as_GPIO(data_pin_id=13,
                                   clock_pin_id=14,
                                   latch_pin_id=15,
                                   initial_pin_values=0x00)
    # Check pin values match initial_pin_values
    for i in range(8):
        assert sr[i] == 0

    # Check setting each pin value updates the pin value
    for i in range(8):
        sr[i] = 1
        assert sr[i] == 1
        sr[i] = 0
        assert sr[i] == 0

    # Check calling shift_out sets the pin values
    for pin_values in range(0xff):
        sr.shift_out(pin_values)
        assert int(sr) == pin_values

    assert len(sr) == 8

    #
    # Test output
    #

    for i in range(8):
        sr.shift_out(0x00)
        assert int(sr) == 0x00

        sr.output(i, 0)
        assert sr.input(i) == 0

    for i in range(8):
        sr.shift_out(0x00)
        assert int(sr) == 0x00

        sr.output(i, 1)
        assert sr.input(i) == 1

    for i in range(8):
        sr.shift_out(0xff)
        assert int(sr) == 0xff

        sr.output(i, 0)
        assert sr.input(i) == 0


if __name__ == '__main__':
    main()

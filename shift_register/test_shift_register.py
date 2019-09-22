from shift_register import ShiftRegisterSIPO


def main():
    sr = ShiftRegisterSIPO(data_pin_id=13,
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
        sr[i] = 0
        assert sr[i] == 0

    # Check calling shift_out sets the pin values
    for pin_values in range(0xff):
        sr.shift_out(pin_values)
        assert int(sr) == pin_values

    assert len(sr) == 8


if __name__ == '__main__':
    main()

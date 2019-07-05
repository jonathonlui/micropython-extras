from micropython import const
from shift_register import ShiftRegisterSIPO


OUT = const(0)
IN = const(1)

HIGH = True
LOW = False

RISING = const(1)
FALLING = const(2)
BOTH = const(3)

PUD_OFF = const(0)
PUD_DOWN = const(1)
PUD_UP = const(2)


class ShiftRegisterSIPO_as_GPIO(ShiftRegisterSIPO):
    """Sub-class of ShiftRegisterSIPO with Adafruit GPIO methods.

    Based on Adafruit's GPIO interface.
    (https://github.com/adafruit/Adafruit_Python_GPIO/blob/master/Adafruit_GPIO/GPIO.py) # noqa
    """
    def setup(self, pin, mode, pull_up_down=PUD_OFF):
        """Set the input or output mode for a specified pin.  Mode should be
        either OUT or IN."""
        if mode != OUT:
            raise NotImplementedError('Only supports pin mode = OUT')

    def output(self, pin, value):
        """Set the specified pin the provided high/low value. Value should be
        either HIGH/LOW or a boolean (true = high)."""
        # print('output {} {}'.format(pin, value))
        value = int(value)
        if self[pin] == value:
            return
        self[pin] = value

    def input(self, pin):
        """Returns the value of the specified pin. HIGH/true if the pin is
        pulled high, or LOW/false if pulled low."""
        return self[pin]

    def set_high(self, pin):
        """Set the specified pin HIGH."""
        self.output(pin, HIGH)

    def set_low(self, pin):
        """Set the specified pin LOW."""
        self.output(pin, LOW)

    def is_high(self, pin):
        """Return t/ue if the specified pin is pulled high."""
        return self.input(pin) == HIGH

    def is_low(self, pin):
        """Return true if the specified pin is pulled low."""
        return self.input(pin) == LOW

    def output_pins(self, pins):
        """Set multiple pins high or low at once.  Pins should be a dict of pin
        name to pin value (HIGH/True for 1, LOW/False for 0). All provided pins
        will be set to the given values.
        """
        data = int(self)
        for pin, value in iter(pins.items()):
            data ^= (-value ^ data) & (1 << pin)

        # print('output_pins 0b{:08b} {}'.format(data, pins))
        self.shift_out(data)

    def setup_pins(self, pins):
        """Setup multiple pins as inputs or outputs at once.

        Pins should be a dict of pin name to pin type (IN or OUT).
        """
        # General implementation that can be optimized by derived classes.
        for pin, value in iter(pins.items()):
            self.setup(pin, value)

    def input_pins(self, pins):
        """Read multiple pins specified in the given list and return list of
        pin values.

        GPIO.HIGH/True if the pin is pulled high, or GPIO.LOW/False if
        pulled low.
        """
        # General implementation that can be optimized by derived classes.
        return [self.input(pin) for pin in pins]

    def add_event_detect(self, pin, edge):
        """Enable edge detection events for a particular GPIO channel.

        Pin should be type IN.  Edge must be RISING, FALLING or BOTH.
        """
        raise NotImplementedError

    def remove_event_detect(self, pin):
        """Remove edge detection for a particular GPIO channel.

        Pin should be type IN.
        """
        raise NotImplementedError

    def add_event_callback(self, pin, callback):
        """Add a callback for an event already defined using add_event_detect().

        Pin should be type IN.
        """
        raise NotImplementedError

    def event_detected(self, pin):
        """Returns True if an edge has occured on a given GPIO.

        You need to enable edge detection using add_event_detect() first.
        Pin should be type IN.
        """
        raise NotImplementedError

    def wait_for_edge(self, pin, edge):
        """Wait for an edge.

        Pin should be type IN. Edge must be RISING, FALLING or BOTH.
        """
        raise NotImplementedError

    def cleanup(self, pin=None):
        """Clean up GPIO event detection for specific pin, or all pins if none
        is specified.
        """

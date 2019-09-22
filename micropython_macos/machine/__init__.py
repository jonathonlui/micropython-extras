import os
import utime

try:
    from micropython import const
except ImportError:
    def const(x): return x

IDLE = const(0)
SLEEP = const(1)
DEEPSLEEP = const(2)

PWRON_RESET = const(0)
HARD_RESET = const(1)
WDT_RESET = const(2)
DEEPSLEEP_RESET = const(3)
SOFT_RESET = const(4)


class ADC:
    def read(self):
        return 0
        # raise NotImplementedError


class Pin:
    OUT = const(0)
    IN = const(1)
    OPEN_DRAIN = const(2)
    ALT = const(3)
    ALT_OPEN_DRAIN = const(4)

    PULL_UP = const(0)
    PULL_DOWN = const(1)

    LOW_POWER = const(0)
    MED_POWER = const(1)
    HIGH_POWER = const(2)

    IRQ_FALLING = const(0)
    IRQ_RISING = const(1)
    IRQ_LOW_LEVEL = const(2)
    IRQ_HIGH_LEVEL = const(3)

    def __init__(self, pin_id, mode=-1, pull=-1, *,
                 value=None, drive=None, alt=None):
        self._pin_id = pin_id
        self.init(mode, pull, value=value, drive=drive, alt=alt)

    def __call__(self, value=None):
        return self.value(value)

    def init(self, mode=-1, pull=-1, *, value=None, drive=None, alt=None):
        self.mode(mode)
        self.pull(pull)
        self.value(value or 0)

    def value(self, value=None):
        if value is None:
            return self._value
        self._value = 1 if value else 0

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)

    def mode(self, mode=None):
        if mode is None:
            return self._mode
        self._mode = mode

    def pull(self, pull):
        if pull is None:
            return self._pull
        self._pull = pull

    def drive(self, drive=None):
        raise NotImplementedError

    def irq(self, *args, **kwargs):
        raise NotImplementedError


class Signal:
    def __init__(self, pin_obj, invert=False, *args, **kwargs):
        if type(pin_obj) == Pin:
            self._pin_obj = pin_obj
        else:
            self._pin_obj = Pin(pin_obj, *args, **kwargs)

        self._invert = invert

    def value(self, x=None):
        if x is not None:
            self._pin_obj.value(x if self._invert else not x)
        else:
            if self._invert:
                return not self._pin_obj.value()
            else:
                return self._pin_obj.value()

    def on(self):
        self.value(True)

    def off(self):
        self.value(False)


class UART:
    def __init__(self, id, *args, **kwargs):
        self.init(*args, **kwargs)

    def init(self, baudrate=9600, bits=8, parity=None, stop=1):
        raise NotImplementedError

    def deinit(self):
        raise NotImplementedError

    def read(self, nbytes=None):
        raise NotImplementedError

    def readinto(self, buf, nbytes=None):
        raise NotImplementedError

    def write(self, buf):
        raise NotImplementedError

    def sendbreak(self):
        raise NotImplementedError


class SPI:
    MASTER = const(0)

    MSB = const(0)
    LSB = const(1)

    def __init__(self, id, *args, **kwargs):
        self.init(*args)

    def init(self, baudrate=1000000,  polarity=0, phase=0, bits=8,
             firstbit=MSB, sck=None, mosi=None, miso=None, pins=None):
        raise NotImplementedError

    def deinit(self):
        raise NotImplementedError

    def read(self, nbytes, write=0x00):
        raise NotImplementedError

    def readinto(self, buf, write=0x00):
        raise NotImplementedError

    def write(self, buf):
        raise NotImplementedError

    def write_readinto(self, write_buf, read_buf):
        raise NotImplementedError


class I2C:
    def __init(self, id=-1, scl=None, sda=None, freq=400000, *args):
        self.init(scl, sda, freq, *args)

    def init(self, scl, sda, freq=400000, *args):
        raise NotImplementedError

    def deinit(self):
        raise NotImplementedError

    def scan(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def readinto(self, buf, nack=True):
        raise NotImplementedError

    def write(self, buf):
        raise NotImplementedError

    def readfrom(self, addr, nbytes, stop=True):
        raise NotImplementedError

    def readfrom_into(self, addr, buf, stop=True):
        raise NotImplementedError

    def writeto(self, addr, buf, stop=True):
        raise NotImplementedError

    def readfrom_mem(self, addr, memaddr, nbytes, addrsize=8, *args):
        raise NotImplementedError

    def readfrom_mem_into(self, addr, memaddr, buf, addrsize=8, *args):
        raise NotImplementedError

    def writeto_mem(self, addr, memaddr, buf, addrsize=8, *args):
        raise NotImplementedError


class RTC:
    ALARM0 = const(0)

    def __init__(self, id=0, *args):
        pass

    def init(self, datetime):
        raise NotImplementedError

    def deinit(self):
        raise NotImplementedError

    def datetime(self):
        return self.now()

    def now(self):
        return utime.localtime()

    def alarm(self, id, time, repeat=False, *args):
        raise NotImplementedError

    def alarm_left(self, alarm_id=0):
        raise NotImplementedError

    def cancel(self, alarm_id=0):
        raise NotImplementedError

    def irq(self, trigger, handler=None, wake=IDLE, *args):
        raise NotImplementedError


class Timer:
    ONE_SHOT = const(0)
    PERIODIC = const(1)

    def __init__(self, id=0, *args):
        raise NotImplementedError

    def deinit(self):
        pass


class WDT:
    def __init__(self, id=0, timeout=5000):
        raise NotImplementedError

    def feed(self):
        raise NotImplementedError


"""
Reset related functions
"""


def reset():
    raise NotImplementedError


def reset_cause():
    return PWRON_RESET


"""
Interrupt related functions
"""


def disable_irq():
    raise NotImplementedError


def enable_irq(state):
    raise NotImplementedError


"""
Power related functions
"""


def freq(frequency=None):
    cmd = 'sysctl hw.cpufrequency'
    _, value = os.popen(cmd).read().split()
    return int(value)


def idle():
    pass


def unique_id():
    # Mac system serial number. See: https://apple.stackexchange.com/a/40244
    cmd = "ioreg -c IOPlatformExpertDevice  -d 2 | " \
        "awk '/IOPlatformSerialNumber/{gsub(/\"/, \"\", $3);  print $3}'"
    return os.popen(cmd).read().strip()


def sleep():
    raise NotImplementedError


def deepsleep():
    raise NotImplementedError

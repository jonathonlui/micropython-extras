# MicroPython-specific Libraries for macOS

[MicroPython](https://github.com/micropython/micropython)  `machine` and `network` modules for macOS

These versions of the modules rely on built-in macOS system commands (e.g. `ifconfig`) to implement the expected behavior of the modules. These system commands are executed using `os.popen` and the output of the commands are parsed for the relevant information.

# Requirements

- [micropython for unix (for macOS)](https://github.com/micropython/micropython#the-unix-version). Install using Homebrew: `brew install micropython`

# Install to local environment

Install the modules using the include `Makefile`:

``` shell
make install
```

Or manually copy the Python modules in `./src` to the local environment's MicroPython library directory. The library directory is usually `~/.micropython/lib`:

```
cp -a ./src/* ~/.micropython/lib/
```

# Modules:

## `machine`

TODO

## `network`

The `network` module implements the `WLAN` class. It only supports station mode (`STA_IF`). If the class is instantiated with mode is to AP mode (`AP_IF`) it will raise `NotImplementedError`.

This module requires the `micropython-xmltok` library to parse the output of macOS's `airport ` command after scanning for available networks.

Some differences from other MicroPython impelmentations, specifically differences from [ESP8266 WLAN](http://docs.micropython.org/en/latest/esp8266/library/network.html#class-wlan) implementation.

- `WLAN.disconnect()` is not implemented
- `WLAN.scan()` does not include "hidden" wireless networks in the return value
- `WLAN.status()` either returns either `STAT_GOT_IP` or `STAT_IDLE` For `STAT_GOT_IP` it doesn't check if actually it got an IP. It only checks  if the wireless interface connected.
- `WLAN.ifconfig()` is read-only. It does not allow setting any config values.
- `WLAN.config()` only supports returning MAC address. It does not allow setting any config values.




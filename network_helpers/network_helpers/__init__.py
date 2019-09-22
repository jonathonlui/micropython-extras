import machine
from micropython import const
import network
import ubinascii
import urequests_ext
import utime


# http://docs.micropython.org/en/v1.9.2/esp8266/library/network.html#network.wlan.scan
NET_SCAN_SSID_IDX = const(0)
NET_SCAN_BSSID_IDX = const(1)
NET_SCAN_CHAN_IDX = const(2)
NET_SCAN_RSSI_IDX = const(3)
NET_SCAN_AUTH_IDX = const(4)
NET_SCAN_HIDDEN_IDX = const(5)

CAPTIVE_STARBUCKS_URL_PREFIX = b'http://sbux-portal.appspot.com/splash'
CAPTIVE_STARBUCKS_SUBMIT_URL = 'http://sbux-portal.appspot.com/submit'


class WirelessNetworkConnectError(Exception):
    pass


class OpenWirelessNetworkConnectError(WirelessNetworkConnectError):
    pass


def connect_to_ssid(ssid, password='', wlan=None):
    """
    Connect specified wirless network with optional password.

    This funcition blocks until successfully connecting to an open network
    or until it unable to find or connect to any open network.

    Args:
        ssid (str):
        password (str):
        wlan (network.WLAN): WLAN object to use to scan and connect. If not
            provided, will instantiate and use a new WLAN object.

    Raises:
        WirelessNetworkConnectError: If the connection fails.
    """
    if not wlan:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)

    wlan.connect(ssid, password)
    while 1:
        status = wlan.status()
        if status in [network.STAT_IDLE, network.STAT_CONNECTING]:
            continue
        elif status == network.STAT_GOT_IP:
            break
        else:
            raise WirelessNetworkConnectError('wlan.status() == %s' % status)
        machine.idle()


def connect_to_open_wireless_network(wlan=None, force=False):
    """
    Connect to an open wirless network. The function scans for nearby
    open (ie. no auth) wirless networks and tries to connect to each one
    starting with the strongest signal (RSSI). If connection fails, this
    function will try the next strongest open network.

    This funcition blocks until successfully connecting to an open network
    or until it unable to find or connect to any open network.

    Args
        wlan (network.WLAN): WLAN object to use to scan and connect. If not
            provided, will instantiate and use a new WLAN object.
        force (bool): By default this func doesn't scan or connect to a
            network if already connected to a network.

    Returns:
        (str, str): Tuple of SSID and IP address

    Raises:
        OpenWirelessNetworkConnectError: If unable to find or connect to
            an open network.
    """
    if not wlan:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)

    mac_addr = ubinascii.hexlify(wlan.config('mac'), ':').decode('utf8')
    ssid = None

    if not force and wlan.isconnected():
        # TODO (jlui): Return SSID
        return ('', wlan.ifconfig()[0])

    aps = wlan.scan()
    aps = filter(lambda n: n[NET_SCAN_AUTH_IDX] == network.AUTH_OPEN, aps)
    aps = sorted(aps, key=lambda e: e[NET_SCAN_RSSI_IDX], reverse=True)
    if not aps:
        raise OpenWirelessNetworkConnectError('No open wireless networks')

    for ap in aps:
        try:
            connect_to_ssid(ssid=ap[NET_SCAN_SSID_IDX], wlan=wlan)
        except WirelessNetworkConnectError:
            # Try next one
            continue
        try:
            get_past_captive_portal(ssid, wlan.ifconfig()[0], mac_addr)
        except CaptivePortalError:
            continue

        ssid = ap[NET_SCAN_SSID_IDX]
        break
    else:
        raise OpenWirelessNetworkConnectError(
            'Could not connect to any open AP'
        )

    return (ssid, wlan.ifconfig()[0])


class CaptivePortalError(Exception):
    pass


# https://stackoverflow.com/a/14030276
def is_captive():
    try:
        r = urequests_ext.get('http://clients3.google.com/generate_204')
    except OSError as err:
        return (True, err)
    r.close()
    if r.status_code == 204:
        return (False, None)
    elif 300 <= r.status_code <= 399:
        return (True, r.location)
    else:
        return (True, None)


def submit_starbucks_captive_portal(mac_addr):
    r = urequests_ext.post(
        CAPTIVE_STARBUCKS_SUBMIT_URL,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data='clmac=%s&apname=' % mac_addr.replace(':', '%3A'))
    r.close()
    if r.status_code != 200:
        raise CaptivePortalError(r.status_code)


def get_past_captive_portal(ssid, ip_addr, mac_addr):
    captive, redirect_url = is_captive()
    if not captive:
        return

    if redirect_url is False:
        raise CaptivePortalError(
            'Not connected to the Internet and did not get a redirect to a '
            'captive portal.')

    if redirect_url.startswith(CAPTIVE_STARBUCKS_URL_PREFIX):
        submit_starbucks_captive_portal(mac_addr)
    else:
        raise CaptivePortalError(
            'Not connected to the Internet and redirect is to an '
            'unsupported redirect URL: %s' % redirect_url)

    # Getting access to the Internet may take a few seconds after
    # submitting the form on the captive portal.
    start = utime.ticks_ms()
    while is_captive()[0]:
        if utime.ticks_diff(utime.ticks_ms(), start) > 10000:
            raise CaptivePortalError('Could not get past captive portal')
        utime.sleep_ms(1000)


def get_external_ip():
    r = urequests_ext.get('https://icanhazip.com/')
    external_addr = r.text.strip()
    r.close()
    return external_addr

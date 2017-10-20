from micropython import const
import os
import ubinascii

from . import parse_plist_xml


STAT_IDLE = const(0)
STAT_CONNECTING = const(1)
STAT_WRONG_PASSWORD = const(2)
STAT_NO_AP_FOUND = const(3)
STAT_CONNECT_FAIL = const(4)
STAT_GOT_IP = const(5)

STA_IF = const(0)
AP_IF = const(1)

AUTH_OPEN = const(0)
AUTH_WEP = const(1)
AUTH_WPA_PSK = const(2)
AUTH_WPA2_PSK = const(3)
AUTH_WPA_WPA2_PSK = const(4)


class WLAN:
    interface = 'en0'

    def __init__(self, interface_id=STA_IF):
        if interface_id != STA_IF:
            raise NotImplementedError(interface_id)

    def active(self, is_active=None):
        if is_active is not None:
            cmd = 'networksetup -setairportpower %s %s' % (
                self.interface, 'on' if is_active else 'off')
            os.popen(cmd)
        else:
            cmd = 'networksetup -getairportpower %s' % self.interface
            return os.popen(cmd).read().endswith('On\n')

    def connect(self, ssid, password):
        cmd = 'networksetup -setairportnetwork %s "%s" "%s"' % (
            self.interface, ssid, password
        )
        out = os.popen(cmd).read().strip()
        if out:
            raise RuntimeError('Connection error')

    def disconnect(self):
        raise NotImplementedError

    def scan(self):
        cmd = '/System/Library/PrivateFrameworks/' \
            'Apple80211.framework/Versions/' \
            'Current/Resources/airport -s -x'
        xml_str = os.popen(cmd).read()

        retval = []

        for net in parse_plist_xml.parse(xml_str):
            if net.get('WEP'):
                authmode = AUTH_WEP
            elif net.get('RSN_IE') or net.get('WPA_IE'):
                t = 'RSN'
                info = net.get('%s_IE' % t)
                if not info:
                    t = 'WPA'
                    info = net.get('%s_IE' % t)

                uchipers = sorted(info.get('IE_KEY_%s_UCIPHERS' % t, []))

                if uchipers == [2]:
                    authmode = AUTH_WPA_PSK
                elif uchipers == [2, 4]:
                    authmode = AUTH_WPA_WPA2_PSK
                elif uchipers == [4]:
                    authmode = AUTH_WPA2_PSK
                else:
                    raise ValueError('Unknown uciphers: %s',
                                     info.get('IE_KEY_%s_UCIPHERS' % t))
            else:
                authmode = AUTH_OPEN

            hidden = 0

            #  (ssid, bssid, channel, RSSI, authmode, hidden)
            retval.append((
                net['SSID_STR'],
                net['BSSID'],
                net['CHANNEL'],
                net['RSSI'],
                authmode,
                hidden,
            ))
        return retval

    def status(self):
        if self.isconnected():
            return STAT_GOT_IP
        else:
            return STAT_IDLE

    def isconnected(self):
        cmd = 'networksetup -getairportnetwork %s' % self.interface
        out = os.popen(cmd).read()
        if out == 'You are not associated with an AirPort network.\n':
            return False
        elif out.startswith('Current Wi-Fi Network: '):
            # ssid = out[len('Current Wi-Fi Network: '):].strip()
            return True
        else:
            raise ValueError(out)

    def ifconfig(self, ifconfig=None):
        if ifconfig is not None:
            raise NotImplementedError

        cmd = "ifconfig %s | awk '/inet /{print $2, $4}'" % self.interface
        ip, netmask = os.popen(cmd).read().strip().split()

        subnet = '.'.join([str(int(netmask) >> i * 8 & 0xff)
                           for i in range(3, -1, -1)])

        cmd = "route -n get default | awk '/gateway: /{print $2}'"
        gateway = os.popen(cmd).read().strip()

        cmd = "awk '/^nameserver/{print $2}' /etc/resolv.conf"
        dns_servers = os.popen(cmd).read().strip().split()
        dns = dns_servers[0] if len(dns_servers) else ''

        return (ip, subnet, gateway, dns)

    def config(self, *args, **kwargs):
        if args and kwargs:
            raise TypeError('either pos or kw args are allowed')
        if len(args) > 2:
            raise TypeError('can query only one param')
        if len(args) == 1:
            if args[0] == 'mac':
                cmd = "ifconfig %s | awk '/ether/{print $2}'" % self.interface
                mac_hex = os.popen(cmd).read().strip()
                return ubinascii.unhexlify(mac_hex.replace(':', ''))
            elif args[0] in ['essid', 'channel', 'hidden',
                             'authmode', 'password']:
                raise NotImplementedError
            else:
                raise ValueError('unknown config param')

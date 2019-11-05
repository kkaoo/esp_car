# boot.py - by leon

import network
import webrepl
import machine
import utime as time
from config import ssid_key


def do_connect(ifconfig=None, reconnection=False):
    '''
    连接WIFI函数
    :param ifconfig: 如果需要指定IP，那么设置ifconfig
    :param reconnection: 如果需要断开重新连接，比如要重新分配IP，那么设为true
    :return:
    '''
    nic = network.WLAN(network.STA_IF)

    if not ssid_key:
        nic.active(False)
        print('boot.py: no found config.ssid_key')
        return
    if len(ssid_key) <= 0:
        nic.active(False)
        print('boot.py: config.ssid_key is Empty')
        return

    nic.active(True)
    if nic.isconnected() and reconnection:
        nic.disconnect()
        time.sleep(1)

    n = 0
    while not nic.isconnected():
        aps = nic.scan()
        for x in aps:
            (ssid, bssid, channel, RSSI, authmode, hidden) = x
            ssid = ssid.decode()
            if ssid in ssid_key.keys():
                print('boot.py: connecting to network: ', ssid, ssid_key[ssid])
                if ifconfig is not None:
                    nic.ifconfig(ifconfig)
                    print('boot.py: IFConfig:', ifconfig)
                nic.connect(ssid, ssid_key[ssid])
                while not nic.isconnected() or nic.ifconfig()[0] == '0.0.0.0':
                    time.sleep(1)
                break
        time.sleep(1)
        n += 1
        if n >= 2:
            print('boot.py: wifi scan timeout..')
            break


if __name__ == '__main__':
    print()
    print()
    print('------welcome to esp car!------')
    do_connect(reconnection=True)
    webrepl.start()
    print('boot.py: running...  ok!')

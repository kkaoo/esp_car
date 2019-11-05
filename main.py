# main.py - by leon

# import os
import time
# from machine import Pin, I2C, SPI
import machine
import network
# import socket
# import select

import boot
import config as cfg
import udp_client
import car
# import remote_control
from key import Key


mode = 'AP-IF'

if __name__ == '__main__':
    print('main.py: ', cfg.board, cfg.name, 'running........')
    if machine.freq() <= 160000000:
        machine.freq(160000000)

    if cfg.name == 'remote_control':
        key4 = Key(4)
        key5 = Key(5)

        uc = None
        ap = network.WLAN(network.AP_IF)
        ap.active(False)

        sta = network.WLAN(network.STA_IF)

        print('main.ap:', ap.ifconfig())
        print('main.sta-if:', sta.ifconfig())

        if sta.ifconfig()[2] == '192.168.4.1':
            uc = udp_client.UdpClient('1')  # 直连方式对方IP需要设为1
        else:
            uc = udp_client.UdpClient()

        send_count = 0
        while True:
            time.sleep_ms(10)
            if key4.value() != Key.NO_KEY or key5.value() != Key.NO_KEY:
                send_count = 10

            # speed = -1000 ~ 1000
            if send_count != 0:
                send_count -= 1
                speed_l = 0
                speed_r = 0
                if key4.value() == Key.VDD:
                    speed_l = -300
                    speed_r = 300
                elif key4.value() == Key.GND:
                    speed_l = 300
                    speed_r = -300
                else:
                    if key5.value() == Key.VDD:
                        speed_l = 500
                        speed_r = 500
                    elif key5.value() == Key.GND:
                        speed_l = -500
                        speed_r = -500

                uc.send(('control_cmd:speed_l='+str(speed_l)+':speed_r='+str(speed_r)).encode())
                time.sleep_ms(90)
    else:
        print('main.py : ESP32 & ESP8266')
        ap = network.WLAN(network.AP_IF)  # create access-point interface
        ap.config(essid='ROBOT', password='robotrobot')
        ap.active(True)  # activate the interface

        # 如果连接到局域网，设置固定IP xx:xx:xx:13
        sta = network.WLAN(network.STA_IF)
        ifconfig = sta.ifconfig()
        if ifconfig[0] != '0.0.0.0':
            new_ip = ifconfig[3][:-1] + '13'
            new_ifc = (new_ip, ifconfig[1], ifconfig[2], ifconfig[3])
            boot.do_connect(ifconfig=new_ifc, reconnection=True)

        car.run()

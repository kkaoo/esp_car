"""
car.py - by leon
v0.1  first version
v0.2  加入html_listen

"""
import socket
import machine
import utime as time
import network
import select
from key import Key
from machine import Pin, PWM, Timer
from html_listen import HtmlListen


# mt_l1 ---- motor left +
# mt_l2 ---- motor left -
# mt_r1 ---- motor left +
# mt_r2 ---- motor left -

# gpio16 ---- LED1

# gpio13 ---- IR Left
# gpio15 ---- IR Right


speed = 500
cmd_count = 0

def pin_init():
    global mt_l1, mt_l2, mt_r1, mt_r2, led1
    if machine.freq() <= 160000000:

        # 原始IO配置，按最初电路的配置
        # mt_l1 = PWM(Pin(5))
        # mt_l2 = PWM(Pin(4))
        # mt_r1 = PWM(Pin(14))
        # mt_r2 = PWM(Pin(12))

        # 新IO配置，有的时候焊接时，马达接反，左右反转， 直接调整程序更方便一些
        mt_l1 = PWM(Pin(5))
        mt_l2 = PWM(Pin(4))
        mt_r1 = PWM(Pin(12))
        mt_r2 = PWM(Pin(14))

        mt_l1.freq(100)
        mt_l2.freq(100)
        mt_r1.freq(100)
        mt_r2.freq(100)

        # 指示灯
        led1 = machine.Pin(16, machine.Pin.OUT)

        ir_left = Pin(13, Pin.OUT)
        ir_right = Pin(15, Pin.OUT)
    else:
        mt_l1 = machine.Pin(5, machine.Pin.OUT)
        mt_l2 = machine.Pin(4, machine.Pin.OUT)
        mt_r1 = machine.Pin(2, machine.Pin.OUT)
        mt_r2 = machine.Pin(15, machine.Pin.OUT)

    stop()
    led1_off()


def led1_on():
    led1.off()


def led1_off():
    led1.on()


def motor_control(speed_l=0, speed_r=0):
    if speed_l >= 0:
        mt_l2.duty(0)
    else:
        mt_l1.duty(0)

    if speed_r >= 0:
        mt_r2.duty(0)
    else:
        mt_r1.duty(0)

    time.sleep_ms(10)

    if speed_l >= 0:
        mt_l1.duty(speed_l)
    else:
        mt_l2.duty(0-speed_l)

    if speed_r >= 0:
        mt_r1.duty(speed_r)
    else:
        mt_r2.duty(0-speed_r)

def stop():
    mt_l1.duty(0)
    mt_l2.duty(0)
    mt_r1.duty(0)
    mt_r2.duty(0)


def cmd_process(data=''):
    # print('cmd_process', data)
    if len(data) < 15:
        return
    if data[0:12] != 'control_cmd:':
        return

    cmd_dict = dict()
    cmd = data[12:].split(':')
    for x in cmd:
        fields = x.split('=')
        cmd_dict[fields[0]] = int(fields[1])

    if 'speed_l' in cmd_dict.keys() and 'speed_r' in cmd_dict.keys():
        print('car.good command "speed L & R"')
        cmd_countdown_reset()
        motor_control(cmd_dict['speed_l'], cmd_dict['speed_r'])

    else:
        print('car.command error:', cmd_dict)


def cmd_countdown_reset():
    global cmd_count
    cmd_count = 0


def tim1_run(t):
    global cmd_count
    if cmd_count < 20:
        cmd_count += 1
        if cmd_count >= 8:
            print('car.py : stop')
            stop()

html_cmd = None
html_cmd_timeout = 0
def check_html_cmd(cmd):
    if cmd in ['forward', 'back', 'left', 'right', 'stop']:
        cmd_countdown_reset()
        print('car.py : ', cmd)
        if cmd == 'forward':
            motor_control(500,500)
        elif cmd == 'back':
            motor_control(-500,-500)
        elif cmd == 'left':
            motor_control(-500,500)
        elif cmd == 'right':
            motor_control(500,-500)
        else:
            stop()


def run():
    pin_init()

    tim1 = Timer(-1)
    tim1.init(period=100, mode=Timer.PERIODIC, callback=tim1_run)       #unit ms

    s1 = None
    ip1 = network.WLAN(network.STA_IF).ifconfig()[0]
    ip2 = network.WLAN(network.AP_IF).ifconfig()[0]
    port = 10000

    print('car.ap:', network.WLAN(network.AP_IF).ifconfig())
    print('car.sta-if:', network.WLAN(network.STA_IF).ifconfig())
    
    try:
        # 临听局域网
        s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 建立一个实例
        s1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s1.bind((ip1, port))
        poller1 = select.poll()
        poller1.register(s1, select.POLLIN)
        print('car.bind socket server : ', ip1, port)

        # 临听SOFT-AP
        s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 建立一个实例
        s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s2.bind((ip2, port))
        poller2 = select.poll()
        poller2.register(s2, select.POLLIN)
        print('car.bind socket server : ', ip2, port)


        html_listen = HtmlListen()

        print('car.run : waiting...')
        led_cycle = 0
        while True:
            res = poller1.poll(30)
            if len(res)>0:
                data, addr = s1.recvfrom(1024)           # Receive 1024 byte of data from the socket
                print('car.received:', data,'from',addr)
                s1.sendto('cmd received', addr)                   # send data to addr
                cmd_process(data.decode())

            res = poller2.poll(30)
            if len(res)>0:
                data, addr = s2.recvfrom(1024)           # Receive 1024 byte of data from the socket
                print('car.received:', data,'from',addr)
                s2.sendto('cmd received', addr)                   # send data to addr
                cmd_process(data.decode())

            check_html_cmd(html_listen.check())

            # 闪烁提示灯
            led_cycle = (led_cycle + 1) % 30
            led1_on() if led_cycle > 10 else led1_off()

    except Exception as e:
        print('car.run :', e)

    if s1 is not None:
        s1.close()
    tim1.deinit()


if __name__ == '__main__':
    run()
    pass

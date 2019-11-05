# key.py - by leon

from machine import Timer, Pin

key_debug = False

"""
pin_num 通过100R电阻，通过按键连接到VDD
pin_num 通过按键连接到GND
"""


class Key:
    VDD = 1
    GND = 0
    NO_KEY = -1

    def __init__(self, pin_num, debounces_ms=30):
        self.debounces = debounces_ms
        self.key_trigger_vdd = False
        self.key_trigger_gnd = False

        self.__scan_step = 0
        self.__pin = Pin(pin_num, Pin.IN)
        self.__st = [0, 1]
        self.__deb = [0, 0]
        self.__pin_num = pin_num

        self.__tim = Timer(-1)
        self.__tim.init(period=10, mode=Timer.PERIODIC, callback=self.__key_scan)

    def __edge_check(self, index, rising_edge=True):
        rising_edge = 0 if rising_edge is True else 1
        ret = False
        value = self.__pin.value()
        if value == self.__st[index]:
            self.__deb[index] = 0
        else:
            self.__deb[index] += 1
            debs = self.debounces/10
            if debs < 2:
                debs = 2
            if self.__deb[index] >= debs:
                self.__deb[index] = 0
                if rising_edge != self.__st[index]:
                    ret = True
                    if key_debug:
                        print('key %d -> %d is triggered' % (self.__pin_num,rising_edge))
                self.__st[index] = value
        return ret

    def __key_scan(self, t):
        step = self.__scan_step
        step += 1
        if step >= 2:
            step = 0

        if step == 0:
            if self.__pin.value():      # filter error level
                self.__deb[1] = 0
            if self.__edge_check(0) is True:
                self.key_trigger_vdd = True
            self.__pin.init(mode=Pin.IN, pull=Pin.PULL_UP)
        elif step == 1:
            if not self.__pin.value():  # filter error level
                self.__deb[0] = 0
            if self.__edge_check(1, rising_edge=False) is True:
                self.key_trigger_gnd = True
            self.__pin.init(mode=Pin.IN, pull=None)
        self.__scan_step = step

    def get_trigger_vdd(self):
        ret = self.key_trigger_vdd
        if ret:
            self.key_trigger_vdd = False
        return ret

    def get_trigger_gnd(self):
        ret = self.key_trigger_gnd
        if ret:
            self.key_trigger_gnd = False
        return ret

    def value(self):
#        print(self.__st)
        if self.__st == [1, 1]:
            return Key.VDD
        elif self.__st == [0, 0]:
            return Key.GND
        else:
            return Key.NO_KEY

    def stop_scan(self):
        self.__tim.deinit()


if __name__ == '__main__':
     # key4 = Key(4)
     # key5 = Key(5)
     # while True:
     #     if key4.get_trigger_vdd():
     #         print('key4 triggered vdd')
     #     if key4.get_trigger_gnd():
     #         print('key4 triggered gnd')
     #     if key5.get_trigger_vdd():
     #         print('key5 triggered vdd')
     #     if key5.get_trigger_gnd():
     #         print('key5 triggered gnd')
     #
     # for i in range(20):
     #     time.sleep_ms(500)
     #     print('key4',key4.value())
     #     print('key5',key5.value())
    pass

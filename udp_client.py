import socket
import network


class UdpClient:
    def __init__(self, host_ip=13, host_port=10000):
        try:
            host_ip = str(host_ip)
            port = host_port + 1
            wlan = network.WLAN(network.STA_IF)
            ip = wlan.ifconfig()[0]
            gw = wlan.ifconfig()[2]

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((ip, port))
            print('udp_client.py : bind ', ip, port)

            host_ip= gw[:-1] + host_ip
            self.host = (host_ip, host_port)
            self.s = s
            self.wlan = wlan
            print('udp_client.py : start ', host_ip, host_port)

        except():
            if s:
                s.close()

    def send(self, data):
        try:
            if self.wlan.isconnected() and self.wlan.ifconfig()[0]!='0.0.0.0':
                self.s.sendto(data, self.host)
                print('udp_client.py : ',data)
            else:
                print('udp_client.run :',self.wlan.ifconfig())
        except Exception as e:
            print('udp_client.run :', e)

if __name__ == '__main__':
#    uc = UdpClient()
#    uc.send('tt')
    pass

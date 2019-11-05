import socket
import machine
import time
import network
import os
import select
# import Queue


class HtmlListen:
    def __init__(self):
        try:
            ap_ip = network.WLAN(network.AP_IF).ifconfig()[0]

            listenSocket = socket.socket()
            listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listenSocket.bind((ap_ip, 80))
            listenSocket.listen(1)

            self.s = listenSocket
            self.inputs = [listenSocket]

        except Exception as e:
            print(e)
            self.poller = None

    def check(self):
        inputs = self.inputs
        server = self.s
        cmd = None

        readable, writable, exceptional = select.select(inputs, [], [], 0.03)

        for s in readable:
            file = open('car_control.html','r')
            html = file.read()
            file.close()
            if s is server:
                client, address = server.accept()
                print("html_listen.py: Connection from", address)
                data = client.recv(1024).decode()[0:25]
#                print(data)
                cmd = self.process(data)
                client.send(html)
                client.close()
                

        return cmd

    def process(self, data):
        if data.find('/?CMD=forward') != -1:
            return 'forward'

        if data.find('/?CMD=back') != -1:
            return 'back'

        if data.find('/?CMD=left') != -1:
            return 'left'

        if data.find('/?CMD=right') != -1:
            return 'right'

        if data.find('/?CMD=stop') != -1:
            return 'stop'

        return None


if __name__ == '__main__':

#    html_listen = HtmlListen()
#    while True:
#        cmd = html_listen.check()
#        if cmd is not None:
#            print(cmd)
    pass

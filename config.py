# config.py - by leon


# 配置board名称，可以方便程序中判断
# 其实程序中是用工作频率来分辨是哪个板子，esp8266是80M, esp32是240M
board = 'ESP8266'
# board = 'ESP32'


# remote_control      发送端（手柄）
# car                 接收端（小车）
name = 'car'
# name = 'remote_control'


# WIFI: 如果需要连接到路由器，那么要在这里配置你的 SSID & password
ssid_key = {}

if name == 'remote_control':
    ssid_key = {
        'ROBOT': 'robotrobot'
    }

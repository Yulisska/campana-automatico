import network
import time
import machine
import urequests
import ujson

wlan_networks = {
    "place#A": ['NVK SOFIA', '011235813' ],
    "place#B": ['space4you', 'qwe123!@#'],
    "place#C": ['iPhone', 'Yulisska13'],
}

wlan = network.WLAN(network.STA_IF)
wlan.active(True)


def reconnect(wlan, name='place#C', attempts=10):
    print("Connecting to WLAN network: {} -> ".format(name), end='')
    wlan.connect(*wlan_networks[name])
    led = machine.Pin("LED", machine.Pin.OUT)
    led.on()
    while not wlan.isconnected() and wlan.status() >= 0 and attempts>0:
        print(".", end='')
        #print(wlan.isconnected(), wlan.status(), attempts)
        time.sleep(1)
        attempts = attempts - 1
    #print(wlan.isconnected(), wlan.status(), attempts)
    led.off()
    if attempts < 1 or not wlan.isconnected():
        raise Exception("Cannot connect to the network: ", name)
    return wlan.ifconfig()


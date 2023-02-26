import network
import time
import machine
import urequests
import ujson

wlan_networks = {
    "place#5": ['space4you', 'qwe123!@#'],
    "place#6": ['NVK SOFIA', '011235813'],
    "place#7": ['iPhone Yulia', 'kokoshnukyulichka888'],
    
}

wlan = network.WLAN(network.STA_IF)
wlan.active(True)


def reconnect(wlan, name='place#2'):
    print("Connecting to WLAN network: {}".format(name))
    wlan.connect(*wlan_networks[name])
    led = machine.Pin("LED", machine.Pin.OUT)
    led.on()
    while not wlan.isconnected() and wlan.status() >= 0:
        print("Waiting to connect:")
        time.sleep(1)
    led.off()
    return wlan.ifconfig()


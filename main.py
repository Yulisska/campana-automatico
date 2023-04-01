from ds3231 import *
from wifi import *
from config import ENDPOINT
from google_sheet import read_sheet

relay_pin = 16

led = machine.Pin("LED", machine.Pin.OUT)
ring_pin=machine.Pin(relay_pin, machine.Pin.OUT)

def sync_time():
    import time
    import os

    try:
        print("Sync time over the internet...")
        led.on()
        import ntptime
        print("\tGetting time from NTP server...", end='')
        ntptime.settime()  # this queries the time from an NTP server
        print("OK")
        pico_rtc = machine.RTC()
        print("\tAdjusting to EEST timezone...", end='')
        utc_shift = 3
        tm = utime.localtime(utime.mktime(utime.localtime()) + utc_shift * 3600)
        tm = tm[0:3] + (0,) + tm[3:6] + (0,)
        pico_rtc.datetime(tm)
        print("OK")
        print("\tSetting external clock...", end='')
        rtc.set_time_from_localtime()
        print("OK")
        print("Done")
        led.off()
    except Exception as e:
        print(e)
        print('Could not sync with time server.')
    finally:
        led.off()


def scanning_I2C():
    import machine
    from ds3231 import I2C_SDA, I2C_SCL, I2C_PORT
    sdaPIN = machine.Pin(I2C_SDA)
    sclPIN = machine.Pin(I2C_SCL)

    i2c = machine.I2C(I2C_PORT, sda=sdaPIN, scl=sclPIN, freq=400000)
    print('scanning i2c bus...')
    devices = i2c.scan()

    print("Found: ", len(devices), " devices")

    for d in devices:
        print("Decimal address: ", d, " HEX: ", hex(d))


# Real Time Clock (external)
rtc = ds3231(I2C_PORT, I2C_SCL, I2C_SDA)  # constants defined in ds3231.py

# connecting to WiFi
cfg = [0]
try:
    cfg = reconnect(wlan, name="place#7")  # network defined in wifi.py
except Exception as e:
    print(e)

sync_time()

# Make GET request
import urequests

my_ping = {"addr": "Героїв Крут 27", "comment": "v4.0, IP: {}, ".format(cfg[0])}
timetable = [] # розклад дзвінків
settings = {} # налаштування
import sys

print("Pico W")
print(sys.implementation)

# r = requests.post(request_url, headers = {'content-type': 'application/json'}, data = post_data) #.json()

led = machine.Pin("LED", machine.Pin.OUT)

def print_range(values):
    global timetable
    for r in values:
        tmp = r[0]
        (h, m) = tmp.split(':')
        hour = int(h.strip())
        minute = int(m.strip())
        # print("\t {}:{}".format(hour, minute))
        timetable.append( (hour, minute) )
    print(timetable)
    
def print_settings(values):
    global settings
    for r in values:
        if r[0]:
            try:
                settings[r[0]] = int(r[1])
            except ValueError as err:
                settings[r[0]] = r[1]
        else:
            break
    print(settings)

print("Reading timetable from Google Spreadsheet...")
sheet_id= "1LX25qDzaKKtRPmRFZ9h7ZoTu1UjYz7yCt85Wwz13dbk"
sheet_name= "розклад"
range_name= "B2:B19"
read_sheet(sheet_id, sheet_name, range_name, print_range)


print("Reading settings from Google Spreadsheet...")
sheet_name= "налаштування"
range_name= "A1:B50"
read_sheet(sheet_id, sheet_name, range_name, print_settings)

if True:
    timeout = 10
    while True:
        #        if wlan.isconnected():
        arr = time.localtime()
        comment = my_ping['comment'] + "дата: {}".format(
            "{}-{}-{} {}:{}:{}".format(arr[0], arr[1], arr[2], arr[3], arr[4], arr[5]))
        print("Current time: {}".format(
            "{}-{}-{} {}:{}:{}".format(arr[0], arr[1], arr[2], arr[3], arr[4], arr[5])))
        for (hour, minute) in timetable:
#            print("Checking: {}:{} vs {}:{}".format(arr[3], arr[4], hour, minute))
            if arr[3]==hour:
                if arr[4]==minute:
                    led.on()
                    ring_pin.on()
                    print("ringing...")
                    time.sleep(settings["ring_time"])
                    led.off()
                    print("ringing done...")
                    ring_pin.off()
                    time.sleep(60)

        request_url = 'https://{}/ping.php?addr={}&comment={}'.format(ENDPOINT, my_ping["addr"], comment)
        try:
            led.on()
            r = urequests.get(request_url)  # .json()
            led.off()
            timeout = 10
            # res = requests.post(request_url, data = "{'addr':'foo'}") #.json()
            print(r.content)
            r.close()
        except Exception as e:
            led.off()
            timeout = 10
            print("Connection failure: ", "Is connected: {}, Status: {}\n".format(wlan.isconnected(), wlan.status()))
            reconnect(wlan)
        time.sleep(5)
        arr = time.localtime()
        print("Current time: {}".format(
            "{}-{}-{} {}:{}:{}".format(arr[0], arr[1], arr[2], arr[3], arr[4], arr[5])))

print("it is over here...")
# to do:
# 1. read time table from https://docs.google.com/spreadsheets/d/1LX25qDzaKKtRPmRFZ9h7ZoTu1UjYz7yCt85Wwz13dbk/edit#gid=0
# 2. control LED according to the time table

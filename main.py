from ds3231 import *
from wifi import *
from config import *
from google_sheet import *
from utilities import *

CONNECTED = False # чи є з'єднання з мережею Internet
relay_pin = 16    # пін керування реле
led_pin   = machine.Pin("LED", machine.Pin.OUT)     # пін керування світлодіодом на платі Raspberry Pi Pico W
ring_pin  = machine.Pin(relay_pin, machine.Pin.OUT) # пін керування дзвінком (реле)

my_ping = {"addr": "Героїв Крут 27", "comment": "v4.0"}
timetable = [] # розклад дзвінків
settings = {} # налаштування

# Real Time Clock (external)
rtc = ds3231(I2C_PORT, I2C_SCL, I2C_SDA)  # constants defined in ds3231.py

def is_connected():
    global CONNECTED
    return CONNECTED == True


def sync_time():
    if not is_connected():
        print("Sync time skipped: there is not Internet connection.")
        return

    try:
        import time
        import os
        from utilities import eesttime, localtime_to_dttm_string

        print("Sync time over the internet...")
        led_pin.on()
        import ntptime
        print("\tGetting time from NTP server... ", end='')
        ntptime.settime()  # this queries the time from an NTP server
        print("OK")
        print("\tAdjusting to EEST timezone with DST... ", end='')
        eest_dttm = eesttime()
        print( localtime_to_dttm_string(eest_dttm) )
        print("\tUpdating internal RTC clock...", end='')
        pico_rtc = machine.RTC()
        tm = eest_dttm
        tm = tm[0:3] + (0,) + tm[3:6] + (0,)
        pico_rtc.datetime(tm)
        print("OK")
        print("\tSetting external RTC clock...", end='')
        rtc.set_time_from_localtime()
        print("OK")
        rtc.read_time()
        print("Done")
        led_pin.off()
    except Exception as e:
        print(e)
        print('Could not sync with time server.')
        print('Reading date from external RTC clock...');
    finally:
        led_pin.off()

def connect():
    global CONNECTED
    # connecting to WiFi
    print("[WLAN] connected: ", wlan.isconnected(), " status: ", wlan.status())
    if wlan.isconnected():
        CONNECTED = True
        return wlan.ifconfig()
    else:
        CONNECTED = False
    cfg = [0]
    networks = list(wlan_networks.keys()) # networks are defined in wifi.py
    print(networks)
    attempts = len(networks)
    index = 0
    while attempts > 0:
        attempts = attempts - 1
        #print(attempts)
        network_name = networks[0]
        #print("Trying WLAN network... ", network_name)
        try:
            cfg = reconnect(wlan, network_name)
            CONNECTED = True
            print("Connected!")
            break
        except Exception as e:
            print(e)
            networks.remove(network_name)

    return cfg

def read_google_spreadsheet_data(online=False):
    is_connected = online == True
    print("Reading timetable from Google Spreadsheet...")
    sheet_id = SPREADSHEET_ID
    sheet_name = timetable_sheet_name
    range_name = timetable_range_name
    try:
        global timetable
        timetable = read_sheet(sheet_id, sheet_name, range_name, load_timetable, online=is_connected)
        print(timetable)

        print("Reading settings from Google Spreadsheet...")
        sheet_name= settings_sheet_name
        range_name= settings_range_name
        global settings
        settings = read_sheet(sheet_id, sheet_name, range_name, load_settings, online=is_connected)
        print(settings)
    except Exception as e:
        read_google_spreadsheet_data(online=False)

# OK: discovery of Wifi networks
# TODO: read time from RTC clock if no internet
# TODO: read timetable and settings from local disk if no internet
# TODO: when to recheck internet / settings (same as frequency for re-reading timetable)?

cfg = connect()
sync_time()
read_google_spreadsheet_data(is_connected())

if True:
    timeout = 10
    import urequests
    import sys
    
    last_check_timestamp = utime.time()

    while True:
        refresh_interval = settings["check_updates_time"]
        print("Time till refresh: ", refresh_interval - (utime.time() - last_check_timestamp), " seconds")
        if utime.time() - refresh_interval > last_check_timestamp:
            print("\n\n\nRefreshing data...\n\n\n")
            last_check_timestamp = utime.time()
            if not is_connected():
                connect()
            read_google_spreadsheet_data(is_connected())

        arr = time.localtime()
        dttm = localtime_to_dttm_string(arr)
        comment = my_ping['comment'] + "дата: " + dttm
        
        print("Current time: ", dttm)
        #print(timetable)
        for (hour, minute) in timetable:
            #print("Checking: {}:{} vs {}:{}".format(arr[3], arr[4], hour, minute))
            if arr[3]==hour:
                if arr[4]==minute:
                    led_pin.on()
                    ring_pin.on()
                    print("Ringing...", end='')
                    time.sleep(settings["ring_time"])
                    led_pin.off()
                    print("DONE")
                    ring_pin.off()
                    n = 60
                    print("Delay for {} seconds...".format(n), end='')
                    time.sleep(n)
                    print("DONE")

        if PINGS_ON:
            try:
                led_pin.on()
                request_url = 'https://{}/ping.php?addr={}&comment={}'.format(ENDPOINT, my_ping["addr"], comment)
                r = urequests.get(request_url)  # .json()
                led_pin.off()
                timeout = 10
                # res = requests.post(request_url, data = "{'addr':'foo'}") #.json()
                print(r.content)
                r.close()
            except Exception as e:
                led_pin.off()
                timeout = 10
                print("Connection failure: ", "Is connected: {}, Status: {}\n".format(wlan.isconnected(), wlan.status()))
                connect()
            time.sleep(5)

print("it is over here...")

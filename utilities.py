# utilities.py
def save_csv(filename, values):
    with open(filename, mode='w') as csvfile:
        for row in values:
            for c in row:
                print(c, end=":")
            print(" ")
            csvfile.write(",".join(row) + "\n")

            
def read_csv(filename, delim=','):
    csvdata = []
    import json
    with open(filename, mode='r') as csvfile:
        for line in csvfile:
            csvdata.append(line.rstrip('\n').rstrip('\r').split(delim))
    return csvdata


def save_json(filename, obj):
    import json
    with open(filename, mode='w') as jsonfile:
        jsonfile.write(json.dumps(obj))


def load_json(filename):
    s_ = None
    with open(filename, mode='r') as jsonfile:
        s_ = jsonfile.read()
    import json
    obj = json.loads(s_)
    return obj


def sync_time(rtc):
    import time
    import utime
    import os
    import machine
    
    led = machine.Pin("LED", machine.Pin.OUT)

    try:
        print("Sync time over the internet...")
        led.on()
        import ntptime
        print("\tGetting time from NTP server...", end='')
        ntptime.settime()  # this queries the time from an NTP server
        print("OK")
        pico_rtc = machine.RTC()
        print("\tAdjusting to EEST timezone...", end='')
        utc_shift = 2
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


def get_localtime_string():
    import time
    arr = time.localtime()
    return "{}-{}-{} {}:{}:{}".format(arr[0], arr[1], arr[2], arr[3], arr[4], arr[5])


def convert_to_hm(hours_and_minutes):
    tmp = hours_and_minutes.strip().split(":")
    h = int(tmp[0].strip())
    m = int(tmp[1].strip())
    return (h, m)

# Micropython esp8266
# This code returns the Central European Time (CET) including daylight saving
# Winter (CET) is UTC+1H Summer (CEST) is UTC+2H
# Changes happen last Sundays of March (CEST) and October (CET) at 01:00 UTC
# Ref. formulas : http://www.webexhibits.org/daylightsaving/i.html
#                 Since 1996, valid through 2099
def eesttime():
    import time
    import os    
    
    year = time.localtime()[0]       #get current year
    #print("localtime: ", time.localtime())
    HHMarch   = time.mktime((year,3 ,(31-(int(5*year/4+4))%7),1,0,0,0,0,0)) #Time of March change to EEST
    HHOctober = time.mktime((year,10,(31-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of October change to EEST
    now=time.time()
    #print("Now: ", now, " >>> ", time.localtime(now))
    if now < HHMarch :               # we are before last sunday of march
        eest=time.localtime(now+7200) # EEST: UTC+2H
    elif now < HHOctober :           # we are before last sunday of october
        eest=time.localtime(now+10800) # EEST: UTC+3H
    else:                            # we are after last sunday of october
        eest=time.localtime(now+7200) # EEST: UTC+2H
    return(eest)


def localtime_to_dttm_string(lt):
    arr = lt
    comment = "{}".format("{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(arr[0], arr[1], arr[2], arr[3], arr[4], arr[5]))
    return comment


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
        

def load_timetable(values):
    from config import timetable_json
    fn = timetable_json
    timetable = []
    from utilities import save_json, load_json
    if len(values) > 0:
        for r in values:
            tmp = r[0]
            (h, m) = tmp.split(':')
            hour = int(h.strip())
            minute = int(m.strip())
            # print("\t {}:{}".format(hour, minute))
            timetable.append( (hour, minute) )
        save_json(filename=fn, obj=timetable)  # fresh copy to local storage
    else:
        timetable = load_json(filename=fn) # re-read copy from local storage
    return timetable
    
def load_settings(values):
    from config import settings_json
    fn = settings_json
    settings = {}
    from utilities import save_json, load_json
    if len(values) > 0:
        for r in values:
            print(r)
            if r[0]:
                try:
                    settings[r[0]] = int(r[1])
                except ValueError as err:
                    settings[r[0]] = r[1]
            else:
                break
        save_json(filename=fn, obj=settings)  # fresh copy to local storage
    else:
        settings = load_json(filename=fn) # re-read copy from local storage
    return settings


import re
import datetime
import urllib.request

def get_geomagnetic_data():
    geomagnetic_txt = urllib.request.urlopen('http://services.swpc.noaa.gov/text/daily-geomagnetic-indices.txt').read()
    #solar_txt = urllib.request.urlopen('ftp://ftp.swpc.noaa.gov/pub/indices/DGD.txt').read()
    geomagnetic_txt = geomagnetic_txt.decode('ascii').split('\n')

    # Daily Geomagnetic Data files are updated every 3 hours beginning at 0030UT

    #                  Middle Latitude        High Latitude            Estimated
    #                - Fredericksburg -     ---- College ----      --- Planetary ---
    #    Date        A     K-indices        A     K-indices        A     K-indices
    # 2017 03 07    13  3 3 4 3 2 2 2 2    33  3 5 4 5 5 5 3 3    16  3 3 4 3 3 3 3 3
    # 2017 04 05    -1  1 1 3 1 2-1-1-1    -1  1 2 3 1 1-1-1-1     8  2 1 3 2 1-1-1-1
    pattern = re.compile('^(\d+).(\d+).(\d+)\s+[-0-9 \t]+(\d+)\s+([ -][0-9])([ -][0-9])([ -][0-9])([ -][0-9])([ -][0-9])([ -][0-9])([ -][0-9])([ -][0-9])$')
    res = []
    for line in geomagnetic_txt:
        if line.startswith('#'):
            continue
        if line.startswith(':'):
            continue

        m = pattern.match(line)
        if m:
            date = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            # print(m)
            Kp03 = int(m.group(5))
            Kp06 = int(m.group(6))
            Kp09 = int(m.group(7))
            Kp12 = int(m.group(8))
            Kp15 = int(m.group(9))
            Kp18 = int(m.group(10))
            Kp21 = int(m.group(11))
            Kp24 = int(m.group(12))
            res.append(dict(
                date=date,
                Ap=int(m.group(4)),
                Kp03=None if Kp03 < 0 else Kp03,
                Kp06=None if Kp06 < 0 else Kp06,
                Kp09=None if Kp09 < 0 else Kp09,
                Kp12=None if Kp12 < 0 else Kp12,
                Kp15=None if Kp15 < 0 else Kp15,
                Kp18=None if Kp18 < 0 else Kp18,
                Kp21=None if Kp21 < 0 else Kp21,
                Kp24=None if Kp24 < 0 else Kp24,
            ))
    return res

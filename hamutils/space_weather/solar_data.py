import re
import datetime
import urllib.request

def get_solar_data():
    solar_txt = urllib.request.urlopen('http://services.swpc.noaa.gov/text/daily-solar-indices.txt').read()
    #solar_txt = urllib.request.urlopen('ftp://ftp.swpc.noaa.gov/pub/indices/DSD.txt').read()
    solar_txt = solar_txt.decode('ascii').split('\n')

    # Daily Solar Data files are updated at 0225UT, 0825UT, 1425UT, & 2025UT

    #                           Sunspot       Stanford GOES15
    #             Radio  SESC     Area          Solar  X-Ray  ------ Flares ------
    #             Flux  Sunspot  10E-6   New     Mean  Bkgd    X-Ray      Optical
    #    Date     10.7cm Number  Hemis. Regions Field  Flux   C  M  X  S  1  2  3
    # ---------------------------------------------------------------------------
    # 2017 04 04   94     75      890      0    -999   B5.5  13  0  0  9  0  0  0
    pattern = re.compile('^(\d+).(\d+).(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([0-9-]+)\s+([A-Z0-9.]+)\s+.*')
    res = []
    for line in solar_txt:
        if line.startswith('#'):
            continue
        if line.startswith(':'):
            continue

        m = pattern.match(line)
        if m:
            date = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            res.append(dict(
                date=date,
                sfi=int(m.group(4)),
                sn=int(m.group(5)),
                x_ray_flux=m.group(9)
            ))
    return res

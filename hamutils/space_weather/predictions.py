import re
import datetime
import urllib.request

def get_space_weather_predictions():
    #swp_txt = urllib.request.urlopen('http://services.swpc.noaa.gov/text/3-day-solar-geomag-predictions.txt').read()
    swp_txt = urllib.request.urlopen('ftp://ftp.swpc.noaa.gov/pub/latest/daypre.txt').read()
    swp_txt = swp_txt.decode('ascii').split('\n')

    date = None
    date_pattern = re.compile('^:Prediction_dates:\s+(\d+\s+[a-zA-Z]+\s+\d+)\s+(\d+\s+[a-zA-Z]+\s+\d+)\s+(\d+\s+[a-zA-Z]+\s+\d+)\s*$')
    Ap = None
    Ap_pattern = re.compile('^A_Planetary\s+(\d+)\s+(\d+)\s+(\d+)\s*$')
    sfi = None
    sfi_pattern = re.compile('^\s+(\d+)\s+(\d+)\s+(\d+)\s*$')
    flux_flag = False
    for line in swp_txt:
        if line.startswith('#'):
            continue
        if flux_flag and not sfi:
            m = sfi_pattern.match(line)
            flux_flag = False
            if m:
                sfi = m
                continue
        if not date:
            m = date_pattern.match(line)
            if m:
                date = m
                continue
        if not Ap:
            m = Ap_pattern.match(line)
            if m:
                Ap = m
                continue
        if line.startswith(':10cm_flux:') and not sfi:
            flux_flag = True
            continue

    res = []
    for i in range(1, 4):
        d = datetime.datetime.strptime(date.group(i), "%Y %b %d").date()
        tmp = dict(date=d, sfi=sfi.group(i), Ap=Ap.group(i))
        res.append(tmp)
    return res

# Micropython esp8266
# This code returns the Central European Time (CET) including daylight saving
# Winter (CET) is UTC+1H Summer (CEST) is UTC+2H
# Changes happen last Sundays of March (CEST) and October (CET) at 01:00 UTC
# Ref. formulas : http://www.webexhibits.org/daylightsaving/i.html
#                 Since 1996, valid through 2099

import utime

def cettime(in_sec = False):
    year = utime.localtime()[0]       #get current year
    HHMarch   = utime.mktime((year,3 ,(31-(int(5*year/4+4))%7),1,0,0,0,0,0)) #Time of March change to CEST
    HHOctober = utime.mktime((year,10,(31-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of October change to CET
    now = utime.time()
    if now < HHMarch :               # we are before last sunday of march
        cet = utime.localtime(now+3600) # CET:  UTC+1H
    elif now < HHOctober :           # we are before last sunday of october
        cet = utime.localtime(now+7200) # CEST: UTC+2H
    else:                            # we are after last sunday of october
        cet = utime.localtime(now+3600) # CET:  UTC+1H
    if in_sec:
        return utime.mktime(cet)
    else:
        return cet

''' This Project will be amazing more or less from the greek wine group

Using Ogimet to get a METAR/TAF
and check for correct METAR & TAF using DWD-Guidelines (btw use .txt-file) ??
Finish this until August '''

from datetime import datetime, date, time, timezone
import datetime as dt

from urllib import request
import urllib.request
import os

from pathlib import Path

import numpy as np
import xarray as xr

import pandas as pd


def Generate_request(icao:str,name:str,auto:bool,
        year:int,month:int,day:int,hour:int,minute:int,
        year_f:int,month_f:int,day_f:int,hour_f:int,minute_f:int
    ) -> str:

        #Set conditions...

        base_url = 'https://www.ogimet.com/display_metars2.php?'
        lang = 'en'    #Language
        tipo = 'ALL'
        ord = 'REV'
        nil = 'SI'                             # INCLUDE NIL-Messages
        fmt = 'txt'                            # File-Format from OGIMET
        send = 'send'

        #Create URL
        url = (base_url+'lang='+lang+'&lugar='+icao
               +'&tipo='+tipo+'&ord='+ord+'&nil='+nil+'&fmt='+fmt
               +'&ano='+f'{year}'+'&mes='+f'{month:02d}'+'&day='+f'{day:02d}'+'&hora='+f'{hour:02d}'
               +'&anof='+f'{year_f}'+'&mesf='+f'{month_f:02d}'+'&dayf='+f'{day_f:02d}'
               +'&horaf='f'{hour_f:02d}'+'&minf='+f'{minute_f}'+'&send='+send)

        #url_old = ('https://www.ogimet.com/display_metars2.php?lang=en&lugar=EDDw&tipo=ALL&ord=REV&nil=SI&fmt=txt'
        #       '&ano=2025&mes=04&day=15&hora=07&anof=2025&mesf=04&dayf=16&horaf=07&minf=59&send=send')

        #print(url_old)

        return url

def Get_file(url:str,icao:str,
             year:int,month:int,day:int,hour:int,minute:int,
             year_f:int,month_f:int,day_f:int,hour_f:int,minute_f:int
    ) -> Path:
    ''' This Function gets the requested METAR/TAF file in the txt-format from OGIMET and download it to reduce
    unwanted requests, if you test with the same file.'''

    print("Start to generate File")
    d_path = (icao
              + f'{year}' + '_'
              + f'{month:02d}' + '_'
              + f'{day:02d}' + '_'
              + f'{hour:02d}' + '_'
              + f'{minute:02d}' + '_'
              + f'{year_f}' + '_'
              + f'{month_f:02d}' + '_'
              + f'{day_f:02d}' + '_'
              + f'{hour_f:02d}' + '_'
              + f'{minute_f:02d}'
              + '.txt')
    print(d_path)

    p = Path.cwd() #Get the current directory
    a_path = p.parents[1] / 'data' / d_path #use the parents_directory up to 1 and add the file-directory part

    if os.path.exists(a_path) == False: #test if the ordered file still exists
        print("Try Connect to Ogimet.. This might take a while...")
        connect_to_url = request.urlopen(url)
        url_status = connect_to_url.code
        if url_status == 200:
            urllib.request.urlretrieve(url, a_path)  # This Command save the file into the folder...
            print('Download finished!')
            return a_path
        else:
            print("Source is offline or something went wrong!")
            print(url_status)
            return a_path
    else:
        print('File already exists! No new File was generated!')
        return a_path

def Gen_Metar_from_file(path:Path):
    ''' This Function will generate the METAR & TAF
    from the OGIMET-File and return a METAR-LIST and TAF-LIST '''
    metar_list = []
    taf_list = []
    continue_taf = False

    with open(path,'r') as afile:
          for line in afile:
            if 'Time interval:' in line:
                date_intervall = line
            if 'Latitude:' in line:
                latitude = line
            if 'Longitude:' in line:
                longtude = line
            if 'Altitude:' in line:
                altitude = line
            if 'EDDW' in line:
                icao = line
            if 'METAR' in line and 'SPECI' not in line:
                metar_list.append(line)
            if 'SPECI' in line and 'METAR' not in line:
                metar_list.append(line)
            if 'TAF' in line and 'large' not in line and 'short' not in line:
                taf_list.append(line)
                continue_taf = True
            elif continue_taf == True and '=' not in line:
                taf_list.append(line)
            elif continue_taf == True and '=' in line:
                taf_list.append(line)
                continue_taf = False

    return metar_list, taf_list

def Parse_Metar(metar_list):
    # INITS
    '''This function using the METAR list to get the weather observation, divide it into different parts.'''
    wind_unit = ['KT', 'MPS', 'KMH']

    wind_list = []
    date_list = []
    var_wind_list = []
    vis_list = []
    cloud_list_1 = []
    cloud_list_2 = []
    cloud_list_3 = []
    special_cloud_list = []
    temperature_list = []
    dewpoint_list = []
    sig_weather_list = []
    pressure_list = []
    trend_list = []

    auto_mode = False
    cavok_mode = False
    wind_mode = False
    latest_idx = 0
    got_wind = -99
    got_wind_var = -99
    got_cloud_1 = -99
    got_cloud_2 = -99
    got_cloud_3 = -99
    got_special_cloud = -99
    got_sig_weather = -99
    got_vis = -99
    got_temp = -99
    got_pressure = -99
    got_trend = -99

    i = 0

    for metar in metar_list:

        # print(i,metar)
        i = i + 1
        # date = metar[0:13]
        date = datetime(int(metar[0:4]),
                        int(metar[4:6]),
                        int(metar[6:8]),
                        int(metar[8:10]),
                        int(metar[10:13])
                        )
        date_list.append(date)

        #print(metar)

        if 'AUTO' in metar:
            auto_mode = True
        for unit in wind_unit:
            if unit in metar:
                wind_mode = unit
                break
        if 'CAVOK' in metar:
            cavok_mode = True

        idx_list = []

        for idx in range(13, len(metar)):
            if metar[idx] == ' ':
                idx_list.append(idx)
                #print(metar[latest_idx:idx])

                if cavok_mode == True:
                    if (got_wind>0 and 'V' not in metar[got_wind:got_wind+5]
                            and got_vis<0) :
                        vis_list.append('CAVOK')
                        cloud_list_1.append('CAVOK')
                        cloud_list_2.append('CAVOK')
                        cloud_list_3.append('CAVOK')
                        special_cloud_list.append('CAVOK')
                        sig_weather_list.append('CAVOK')
                        got_vis = idx
                        got_sig_weather = idx
                        got_cloud_1 = idx
                        got_cloud_2 = idx
                        got_cloud_3 = idx
                        got_special_cloud = idx
                        got_sig_weather = idx
                else:
                    if got_wind>0 and 'V' not in metar[got_wind:got_wind+5]:
                        vis_list.append(metar[latest_idx:idx])

                if (got_wind>0
                        and 'V' in metar[got_wind:got_wind+5]
                        and got_wind_var<0
                ):
                    if cavok_mode == False:
                        var_wind_list.append(metar[latest_idx:idx])
                        got_wind_var = idx
                    else:
                        if 'CAVOK' in metar[got_wind:got_wind+6]:
                            var_wind_list.append('-99V-99')
                            got_wind_var = idx
                        else:
                            var_wind_list.append(metar[latest_idx:idx])
                            got_wind_var = idx


                if wind_mode in metar[latest_idx:idx] and got_wind<0:
                    wind_list.append(metar[latest_idx:idx])
                    got_wind = idx

                latest_idx = idx

        if got_wind_var<0:
            var_wind_list.append('-99V-99')

        got_wind = -99
        got_wind_var = -99
        got_cloud_1 = -99
        got_cloud_2 = -99
        got_cloud_3 = -99
        got_special_cloud = -99
        got_sig_weather = -99
        got_vis = -99
        got_temp = -99
        got_pressure = -99
        got_trend = -99
        auto_mode = False
        cavok_mode = False
        #print(metar[latest_idx:])

    print(wind_list)
    print(date_list)
    print(var_wind_list)

    #ds = xr.Dataset(
    #    data_vars=dict(wind_list,var_wind_list),
    #    dims=["time"],
    #    coords=dict(time=date_list),
    #    attrs=dict(description='windspeed',
    #               units=f'{wind_mode}'
    #               )
    #    )

    #print(ds)

date = datetime.now()
date2 = datetime.now(timezone.utc)
print(date.strftime('%a %d %b %Y %H:%M'))
print(date2.strftime('%a %d %b %Y %H:%M'))

flugplatz = 'EDDW'
stadt = 'Bremen'
automat = True
year = 2025
month = 6
day = 7
hour = 11
minute = 0
year_f = 2025
month_f = 6
day_f = 8
hour_f = 9
minute_f = 59




url = Generate_request(flugplatz,stadt,automat,
                       year,month,day,hour,minute,
                       year_f,month_f,day_f,hour_f,minute_f
                       )

path = Get_file(url,flugplatz,
                year,month,day,hour,minute,
                year_f,month_f,day_f,hour_f,minute_f
                )
metar,taf = Gen_Metar_from_file(path)

Parse_Metar(metar)


# FX,FF,DD
# DD > 60° wenn ff >= 5 KT
# FF >= 5 KT
# BÖE: positive Abweichung von FF>10 KT, wenn t >= 3s
#
# Forcasted Fx oder change of windspeed of forecasted FX um >= 10 KT,
# if FF after change >= 15KT forecasted
#
# VIS-Tresholds :
# -- : >
# ++ : <=
# 0150
# 0350
# 0600
# 0800
# 1500
# 3000
# 5000
# WW:
# (+ /nothing/ -)
# MI/BC/PR/DR/BL/SH/TS/FZ
# DZ/RA/SN/SG/PL/GR/GS/UP
# BR/FG/FU/VA/DU/SA/HZ
# PO/SQ/FC/SS/DS
# TRESHOLD :
# + or nothing
# ever FZ (Freezing)
# ever TS
# SQ (ff >= 16KT increasing >= 21 KT)
# FC
# Other Weather if VIS > 5000
# CLOUDS/COVER
# SKC/NSC 0/8 or Clouds over 5000 FT
# FEW 1/8
# SCT 2/8-4/8
# BKN 5/8-7/8
# OVC 8/8
# If Cloudiness change from FEW/SCT/NSC/SKC to BKN/OVC or the other way around
# and Cloudbase (Ceiling change to treshold)
# Cloudbase (CIG):
# -- : >
# ++ : <=
# 001
# 002
# 005
# 010
# 015
# SPECIAL CASE : VV  (vertical viewrange)
# CAVOK if VIS> 9999 and NSC!


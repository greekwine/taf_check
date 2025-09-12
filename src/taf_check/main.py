''' This Project will be amazing more or less from the greek wine group

Using Ogimet to get a METAR/TAF
and check for correct METAR & TAF using DWD-Guidelines (btw use .txt-file) ??
Finish this until August '''

from datetime import datetime, date, time, timezone
import datetime as dt
from unittest import result

from urllib import request
import urllib.request
import os

from pathlib import Path

import numpy as np
import xarray as xr

import pandas as pd


# ToDO for better readability you could create a dataclass and this becomes the single
#  parameter
def Generate_request(icao:str,name:str,auto:bool,
        year:int,month:int,day:int,hour:int,minute:int,
        year_f:int,month_f:int,day_f:int,hour_f:int,minute_f:int
    ) -> str:

        #Set conditions...

        # ToDo I would set this as a constant at the top
        base_url = 'https://www.ogimet.com/display_metars2.php?'
        lang = 'en'    #Language
        tipo = 'ALL'
        ord = 'REV'
        nil = 'SI'                             # INCLUDE NIL-Messages
        fmt = 'txt'                            # File-Format from OGIMET
        send = 'send'

        #Create URL
        # ToDo try using formatted string only (with the {}) and not a mix between
        #  addition and formatting
        url = (base_url+'lang='+lang+'&lugar='+icao
               +'&tipo='+tipo+'&ord='+ord+'&nil='+nil+'&fmt='+fmt
               +'&ano='+f'{year}'+'&mes='+f'{month:02d}'+'&day='+f'{day:02d}'+'&hora='+f'{hour:02d}'
               +'&anof='+f'{year_f}'+'&mesf='+f'{month_f:02d}'+'&dayf='+f'{day_f:02d}'
               +'&horaf='f'{hour_f:02d}'+'&minf='+f'{minute_f}'+'&send='+send)

        # ToDo rm unused code
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

    # ToDo I would recommend logging instead of printing
    print("Start to generate File")
    # ToDo same here
    d_path = (
        f"{icao}{year}_{month:02d}_{day:02d}_{hour:02d}_{minute:02d}_{year_f}_"
        f"{month_f:02d}_{day_f:02d}_{hour_f:02d}_{minute_f:02d}.txt"
    )

    print(d_path)

    p = Path.cwd() #Get the current directory
    a_path = p.parent / 'data' / d_path #use the parents_directory up to 1 and add the file-directory part

    # ToDo dont compare directly against bools
    if not os.path.exists(a_path): #test if the ordered file still exists
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
        # ToDo the indentation is a bit of (mix between 2, 4, and 6 spaces)
        #  if you like you could try black as an code formatter
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

            # ToDo dont compare against bool
            elif continue_taf and '=' not in line:
                taf_list.append(line)
            elif continue_taf and '=' in line:
                taf_list.append(line)
                continue_taf = False

    return metar_list, taf_list

def vis_check(metar_obj,status_vis,status_vis_min,vis_idx,metar_auto):
    ''' This Function test whether the input is a Visibility or not'''
    # ToDo metar_auto is unused?
    # ToDo I find it hard to get the reason behind the filter. Consider writing some
    #  context why you filter this way

    # ToDo This has a lot of nesting. I think is part is equivalent, and in my opinion
    #  more readable - please check if that is in fact the same
    vis = metar_obj.replace(' ', '')
    if not (len(vis) == 4 and vis.isdigit()):
        raise ValueError(f"Invalid visibility: {vis} is not a 4-digit number.")

    if status_vis < 0:
        return vis, vis_idx, status_vis_min, True

    if status_vis_min < 0:
        return vis, status_vis, vis_idx, True

    raise ValueError("More than two visibilities found! Please check the input.")

    # ToDo end of example
    vis = metar_obj.replace(' ', '')
    found_vis = False

    if len(vis) == 4 and vis.isdigit():
        if status_vis < 0:
            result = vis
            status_vis = vis_idx
            found_vis = True
        else:
            if status_vis_min < 0:
                result = vis
                status_vis_min = vis_idx
                found_vis = True
            else:
                # ToDo consider raising an error like ValueError if you want to
                #  terminate the programm
                print('An error occurred while checking Visibility. There are more than three Visibilities!'
                      'Please check the Input.')
                result = '0'
    else:
        found_vis = False
        result = '0'
        print('An error occurred while checking Visibility: '+vis+' is not a Visibility')

    return found_vis,result,status_vis,status_vis_min

def cloud_check(metar_obj,
                status_cloud_1,
                status_cloud_2,
                status_cloud_3,
                status_sig_cloud,
                cloud_idx,
                auto_mode,
                cloud_list_1,
                cloud_list_2,
                cloud_list_3,
                cloud_list_sig
                ):
    ''' This Function test whether the input is part of the Clouds or not. If it's a detected as a cloud the function
    will add the cloud to the right list (level 1, level 2, level 3 and/or sig. cloud)'''


    cloud_unit = ['BKN', 'OVC', 'SCT', 'FEW', 'NSC', 'SKC', 'VV']
    cloud = metar_obj
    found_cloud = False

    if auto_mode == True:
        for cloudcover in cloud_unit:
            if cloudcover in cloud:
                found_cloud = True
                if status_cloud_1 < 0:
                    status_cloud_1 = cloud_idx
                    cloud_list_1.append(cloud)
                else:
                    if status_cloud_2 < 0 and cloud_idx != status_cloud_1:
                        status_cloud_2 = cloud_idx
                        cloud_list_2.append(cloud)
                    else:
                        if status_cloud_3 < 0 and cloud_idx != status_cloud_1 and cloud_idx != status_cloud_2:
                            status_cloud_3 = cloud_idx
                            cloud_list_3.append(cloud)
                        else:
                            if ('TCU' in cloud or
                                'CB' in cloud):
                                if status_sig_cloud < 0:
                                    status_sig_cloud = cloud_idx
                                    cloud_list_sig.append(cloud)
                                else:
                                    print('Oh here we go :)')
                            else:
                                print('An error occurred while checking Clouds. There are more to many Clouds...'
                                      'Please check the Input! ')

    if found_cloud == False:
        print('There is a Problem '+ cloud + ' is not a cloud...')

    return (found_cloud,
            status_cloud_1,
            status_cloud_2,
            status_cloud_3,
            status_sig_cloud,
            cloud_list_1,
            cloud_list_2,
            cloud_list_3,
            cloud_list_sig)

def weather_check(metar_obj,
                  status_wx_1,
                  status_wx_2,
                  status_wx_3,
                  wx_idx,
                  auto_mode,
                  list_wx_1,
                  list_wx_2,
                  list_wx_3
                  ):

    ''' This Function test whether the input is Part of WX or not. If it's a detected as a weather the function
        will add the weather to the list (wx 1, wx 2 or wx 3).'''

    cloud_unit = ['BKN', 'OVC', 'SCT', 'FEW', 'NSC', 'SKC']

    wx_unit = ['MI', 'BC', 'PR', 'DR', 'BL', 'SH', 'TS', 'FZ', 'DZ', 'RA', 'SN', 'SG'
        , 'PL', 'GR', 'GS', 'UP', 'BR', 'FG', 'FU', 'VA', 'DU', 'SA', 'HZ', 'PO'
        , 'SQ', 'FC', 'SS', 'DS', 'WS', 'IC', 'PY', 'VC', 'RE']

    found_wx = False
    weather = metar_obj
    if auto_mode == True or auto_mode == False:
        for wx in wx_unit:
            if wx in weather and wx not in cloud_unit:
                found_wx = True
                if status_wx_1 < 0:
                    status_wx_1 = wx_idx
                    list_wx_1.append(weather)
                else:
                    if status_wx_2 < 0 and wx_idx != status_wx_1:
                        status_wx_2 = wx_idx
                        list_wx_2.append(weather)
                    else:
                        if status_wx_3 < 0 and wx_idx != status_wx_2 and wx_idx != status_wx_1:
                            status_wx_3 = wx_idx
                            list_wx_3.append(weather)
                        else:
                            print('An error occurred while checking weathers. There are more then three weathers '
                                  'detected. Check input file!')
            else:
                if weather in cloud_unit:
                    print('Error: This Weather is a Cloud. Check if clouds are all detected. '+weather)

    if found_wx == False:
        print('There is a Problem '+ weather + ' is not a Weather...')

    return (found_wx,
            list_wx_1,
            list_wx_2,
            list_wx_3,
            status_wx_1,
            status_wx_2,
            status_wx_3)

def temp_tau_check(metar_obj,temp_status,temp_list,dew_point_list,temp_idx):

    ''' This Function checks if there is any Temperature or Dewpoint values and if the are some values, it will add to
    the temperature and dewpoint list'''

    #Struture : 00/00 or M01/M07
    temp_tau = metar_obj.replace(' ','')
    found_temp = False
    if "/" in temp_tau and len(temp_tau) == 5:
        temp_list.append(temp_tau[:2])
        dew_point_list.append(temp_tau[3:])
        found_temp = True
        temp_status = temp_idx

    elif "/" in temp_tau and 'M' in temp_tau:
        temp_list.append(temp_tau[:3])
        dew_point_list.append(temp_tau[4:])
        found_temp = True
        temp_status = temp_idx

    return (found_temp,
            temp_status,
            temp_list,
            dew_point_list)

def Parse_Metar(metar_list):
    # INITS

    '''This function using the METAR list to get the weather observation, divide it into different parts and save the
    parts into a file. This contains all the Metar-Information'''

    wind_unit = ['KT', 'MPS', 'KMH']
    pressure_unit = ['Q']
    #cloud_unit = ['BKN','OVC','SCT','FEW','NSC','SKC']
    wx_unit = ['MI','BC','PR','DR','BL','SH','TS','FZ','DZ','RA','SN','SG'
                ,'PL','GR','GS','UP','BR','FG','FU','VA','DU','SA','HZ','PO'
                ,'SQ','FC','SS','DS','WS','IC','PY','VC','RE']

    wind_list = []
    date_list = []
    var_wind_list = []

    vis_list = []
    vis_min_list = []

    cloud_list_1 = []
    cloud_list_2 = []
    cloud_list_3 = []
    special_cloud_list = []

    temperature_list = []
    dewpoint_list = []

    sig_weather_list = []
    sig_weather_list_2 = []
    sig_weather_list_3 = []

    pressure_list = []
    trend_list = []

    auto_mode = False
    cavok_mode = False
    wind_mode = ''
    latest_idx = 0
    got_wind = -99
    got_wind_var = -99
    got_cloud_1 = -99
    got_cloud_2 = -99
    got_cloud_3 = -99
    got_special_cloud = -99
    got_sig_weather = -99
    got_sig_weather_2 = -99
    got_sig_weather_3 = -99
    got_vis = -99
    got_vis_min = -99
    got_temp = -99
    got_pressure = -99
    got_trend = -99

    i = 0

    # ToDo the following lines are quite nested and hard to overview.
    #  maybe you find a way ato simplify this and/or introduce small function for parts
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
            #Automatic Stations can't observe everything, often the structure differs compared to human generated
            # - Parser need to be adjust
            auto_mode = True
        for unit in wind_unit:
            #Some Nations use different windspeed-units. We use the shortcuts to find the wind parameter
            if unit in metar:
                wind_mode = unit
                break
        if 'CAVOK' in metar:
            #"CAVOK is special, cause Visibility, Cloudiness, Weather are described by this word and the structure of
            # the Metar differs by using from typical structures.
            cavok_mode = True

        idx_list = []

        #Start Parsing over the metar....

        for idx in range(13, len(metar)):
            if metar[idx] == ' ':

                #Spacing in METAR will change the part of the METAR and his information.

                idx_list.append(idx)

                print(metar[latest_idx:idx])

                #Windgroupe

                if wind_mode in metar[latest_idx:idx] and got_wind < 0:
                    wind_list.append(metar[latest_idx:idx])
                    got_wind = idx

                    if 'V' in metar[got_wind:got_wind+5]:
                        if 'CAVOK' in metar[got_wind:got_wind + 6] or 'VV' in metar[got_wind:got_wind + 6]:
                            var_wind_list.append('-99V-99')
                            got_wind_var = idx
                        else:
                            var_wind_list.append(metar[got_wind:got_wind + 8])
                            got_wind_var = got_wind + 8
                    else:
                        var_wind_list.append('-99V-99')
                        got_wind_var = idx

                if cavok_mode == True:
                    #CAVOK means no clouds, Vis over 10km, No Weather and no special clouds...
                    if (got_wind>0
                        and got_vis<0
                        and idx != got_wind_var
                        and idx != got_wind):
                        #Adjust Parser

                        vis_list.append('CAVOK')
                        vis_min_list.append('CAVOK')
                        cloud_list_1.append('CAVOK')
                        cloud_list_2.append('CAVOK')
                        cloud_list_3.append('CAVOK')
                        special_cloud_list.append('CAVOK')
                        sig_weather_list.append('CAVOK')
                        sig_weather_list_2.append('CAVOK')
                        sig_weather_list_3.append('CAVOK')

                        got_vis = idx
                        got_vis_min = idx

                        got_cloud_1 = idx
                        got_cloud_2 = idx
                        got_cloud_3 = idx

                        got_special_cloud = idx
                        got_sig_weather = idx
                        got_sig_weather_2 = idx
                        got_sig_weather_3 = idx
                else: #In Case there is no Cavok...
                    if got_wind>0 and idx != got_wind_var and idx != got_wind:
                        if got_vis<0 or got_vis_min<0:
                            found_vis,vis,got_vis,got_vis_min = vis_check(metar[latest_idx:idx],
                                                                          got_vis,
                                                                          got_vis_min,
                                                                          idx,
                                                                          auto_mode)
                            if found_vis == True:
                                if got_vis_min < 0 :
                                    vis_list.append(vis)
                                elif got_vis_min > 0 :
                                    vis_min_list.append(vis)
                            else:
                                if got_sig_weather < 0 or got_sig_weather_2 < 0 or got_sig_weather_3 < 0 :
                                    #Test for WX:
                                    (found_wx,sig_weather_list,sig_weather_list_2,sig_weather_list_3,
                                    got_sig_weather, got_sig_weather_2, got_sig_weather_3) = \
                                    weather_check(metar[latest_idx:idx],
                                                  got_sig_weather,
                                                  got_sig_weather_2,
                                                  got_sig_weather_3,
                                                  idx,
                                                  auto_mode,
                                                  sig_weather_list,
                                                  sig_weather_list_2,
                                                  sig_weather_list_3)
                                    if found_wx == True:
                                        if got_vis_min < 0:
                                            vis_min_list.append('-999')
                                            got_vis_min = idx
                                    else:
                                        (found_cloud,got_cloud_1,got_cloud_2,got_cloud_3,got_special_cloud,
                                        cloud_list_1,cloud_list_2,cloud_list_3,special_cloud_list) = \
                                        cloud_check(metar[latest_idx:idx],got_cloud_1,got_cloud_2,got_cloud_3,
                                                    got_special_cloud,idx,
                                                    auto_mode,
                                                    cloud_list_1,
                                                    cloud_list_2,
                                                    cloud_list_3,
                                                    special_cloud_list)
                                        if found_cloud == True:
                                            if got_sig_weather < 0:
                                                sig_weather_list.append('NO WX')
                                                got_sig_weather = idx
                                            if got_sig_weather_2 < 0:
                                                sig_weather_list_2.append('NO WX')
                                                got_sig_weather_2 = idx
                                            if got_sig_weather_3 < 0:
                                                sig_weather_list_3.append('NO WX')
                                                got_sig_weather_3 = idx
                                            if got_vis_min < 0:
                                                vis_min_list.append('-999')
                                                got_vis_min = idx

                        elif got_vis_min < 0 and got_vis > 0:
                            found_vis, vis, got_vis, got_vis_min = vis_check(metar[latest_idx:idx],
                                                                             got_vis,
                                                                             got_vis_min,
                                                                             idx,
                                                                             auto_mode)
                            if found_vis == True:
                                got_vis_min = idx
                                vis_min_list.append(vis)
                            else:
                                if got_sig_weather < 0 or got_sig_weather_2 < 0 or got_sig_weather_3 < 0:
                                    (found_wx, sig_weather_list, sig_weather_list_2, sig_weather_list_3,
                                     got_sig_weather, got_sig_weather_2, got_sig_weather_3) = \
                                        weather_check(metar[latest_idx:idx],
                                                      got_sig_weather,
                                                      got_sig_weather_2,
                                                      got_sig_weather_3,
                                                      idx,
                                                      auto_mode,
                                                      sig_weather_list,
                                                      sig_weather_list_2,
                                                      sig_weather_list_3)
                                    if found_wx == True:
                                        if got_vis_min < 0:
                                            vis_min_list.append('-999')
                                            got_vis_min = idx
                                    else:
                                        (found_cloud, got_cloud_1, got_cloud_2, got_cloud_3, got_special_cloud,
                                         cloud_list_1, cloud_list_2, cloud_list_3, special_cloud_list) = \
                                            cloud_check(metar[latest_idx:idx], got_cloud_1, got_cloud_2, got_cloud_3,
                                                        got_special_cloud, idx,
                                                        auto_mode,
                                                        cloud_list_1,
                                                        cloud_list_2,
                                                        cloud_list_3,
                                                        special_cloud_list)
                                        if found_cloud == True:
                                            if got_sig_weather < 0:
                                                sig_weather_list.append('NO WX')
                                                got_sig_weather = idx
                                            if got_sig_weather_2 < 0:
                                                sig_weather_list_2.append('NO WX')
                                                got_sig_weather_2 = idx
                                            if got_sig_weather_3 < 0:
                                                sig_weather_list_3.append('NO WX')
                                                got_sig_weather_3 = idx
                                            if got_vis_min < 0:
                                                vis_min_list.append('-999')
                                                got_vis_min = idx
                        else:
                            if got_sig_weather < 0 or got_sig_weather_2 < 0 or got_sig_weather_3 < 0:
                                (found_wx, sig_weather_list, sig_weather_list_2, sig_weather_list_3,
                                 got_sig_weather, got_sig_weather_2, got_sig_weather_3) = \
                                 weather_check(metar[latest_idx:idx],
                                               got_sig_weather,
                                               got_sig_weather_2,
                                               got_sig_weather_3,
                                               idx,
                                               auto_mode,
                                               sig_weather_list,
                                               sig_weather_list_2,
                                               sig_weather_list_3)
                                if found_wx == True:
                                    if got_vis_min < 0:
                                        vis_min_list.append('-999')
                                        got_vis_min = idx
                                else:
                                    (found_cloud, got_cloud_1, got_cloud_2, got_cloud_3, got_special_cloud,
                                     cloud_list_1, cloud_list_2, cloud_list_3, special_cloud_list) = \
                                        cloud_check(metar[latest_idx:idx], got_cloud_1, got_cloud_2, got_cloud_3,
                                                    got_special_cloud, idx,
                                                    auto_mode,
                                                    cloud_list_1,
                                                    cloud_list_2,
                                                    cloud_list_3,
                                                    special_cloud_list)
                                    if found_cloud == True:
                                        if got_sig_weather < 0:
                                            sig_weather_list.append('NO WX')
                                            got_sig_weather = idx
                                        if got_sig_weather_2 < 0:
                                            sig_weather_list_2.append('NO WX')
                                            got_sig_weather_2 = idx
                                        if got_sig_weather_3 < 0:
                                            sig_weather_list_3.append('NO WX')
                                            got_sig_weather_3 = idx
                                        if got_vis_min < 0 :
                                            vis_min_list.append('-999')
                                            got_vis_min = idx
                if got_vis_min > 0 and got_sig_weather > 0 and got_vis > 0 and got_wind > 0:
                    (found_cloud, got_cloud_1, got_cloud_2, got_cloud_3, got_special_cloud,
                    cloud_list_1, cloud_list_2, cloud_list_3, special_cloud_list) = \
                    cloud_check(metar[latest_idx:idx], got_cloud_1, got_cloud_2, got_cloud_3,
                                got_special_cloud, idx,
                                auto_mode,
                                cloud_list_1,
                                cloud_list_2,
                                cloud_list_3,
                                special_cloud_list)
                    if found_cloud == True:
                        if got_sig_weather < 0:
                            sig_weather_list.append('NO WX')
                            got_sig_weather = idx
                        if got_sig_weather_2 < 0:
                            sig_weather_list_2.append('NO WX')
                            got_sig_weather_2 = idx
                        if got_sig_weather_3 < 0:
                            sig_weather_list_3.append('NO WX')
                            got_sig_weather_3 = idx

                if got_cloud_1 > 0 and idx != got_cloud_1:
                    (found_cloud, got_cloud_1, got_cloud_2, got_cloud_3, got_special_cloud,
                     cloud_list_1, cloud_list_2, cloud_list_3, special_cloud_list) = \
                        cloud_check(metar[latest_idx:idx], got_cloud_1, got_cloud_2, got_cloud_3,
                                    got_special_cloud, idx,
                                    auto_mode,
                                    cloud_list_1,
                                    cloud_list_2,
                                    cloud_list_3,
                                    special_cloud_list)
                    if found_cloud == False:
                        found_temp, got_temp, temperature_list, dewpoint_list = \
                            temp_tau_check(
                                metar[latest_idx:idx],
                                got_temp,
                                temperature_list,
                                dewpoint_list,
                                idx
                            )
                        if found_temp == True and got_temp < 0:
                            if got_cloud_1 < 0:
                                cloud_list_1.append('NIL')
                                got_cloud_1 = idx
                            if got_cloud_2 < 0:
                                cloud_list_2.append('NIL')
                                got_cloud_2 = idx
                            if got_cloud_3 < 0:
                                cloud_list_3.append('NIL')
                                got_cloud_3 = idx
                            if got_special_cloud < 0:
                                special_cloud_list.append('NIL')
                                got_special_cloud = idx
                elif got_cloud_2 > 0 and idx != got_cloud_2:
                    (found_cloud, got_cloud_1, got_cloud_2, got_cloud_3, got_special_cloud,
                     cloud_list_1, cloud_list_2, cloud_list_3, special_cloud_list) = \
                     cloud_check(metar[latest_idx:idx], got_cloud_1, got_cloud_2, got_cloud_3,
                                 got_special_cloud, idx,
                                 auto_mode,
                                 cloud_list_1,
                                 cloud_list_2,
                                 cloud_list_3,
                                 special_cloud_list)
                    if found_cloud == False and got_temp < 0:
                        found_temp, got_temp, temperature_list, dewpoint_list = \
                            temp_tau_check(
                                metar[latest_idx:idx],
                                got_temp,
                                temperature_list,
                                dewpoint_list,
                                idx
                            )
                        if found_temp == True:
                            if got_cloud_1 < 0:
                                cloud_list_1.append('NIL')
                                got_cloud_1 = idx
                            if got_cloud_2 < 0:
                                cloud_list_2.append('NIL')
                                got_cloud_2 = idx
                            if got_cloud_3 < 0:
                                cloud_list_3.append('NIL')
                                got_cloud_3 = idx
                            if got_special_cloud < 0:
                                special_cloud_list.append('NIL')
                                got_special_cloud = idx
                elif got_cloud_3 > 0 and idx != got_cloud_3:
                    (found_cloud, got_cloud_1, got_cloud_2, got_cloud_3, got_special_cloud,
                     cloud_list_1, cloud_list_2, cloud_list_3, special_cloud_list) = \
                        cloud_check(metar[latest_idx:idx], got_cloud_1, got_cloud_2, got_cloud_3,
                                    got_special_cloud, idx,
                                    auto_mode,
                                    cloud_list_1,
                                    cloud_list_2,
                                    cloud_list_3,
                                    special_cloud_list)
                    if found_cloud == False and got_temp < 0:
                        found_temp, got_temp, temperature_list, dewpoint_list = \
                            temp_tau_check(
                                metar[latest_idx:idx],
                                got_temp,
                                temperature_list,
                                dewpoint_list,
                                idx
                            )
                        if found_temp == True:
                            if got_cloud_1 < 0:
                                cloud_list_1.append('NIL')
                                got_cloud_1 = idx
                            if got_cloud_2 < 0:
                                cloud_list_2.append('NIL')
                                got_cloud_2 = idx
                            if got_cloud_3 < 0:
                                cloud_list_3.append('NIL')
                                got_cloud_3 = idx
                            if got_special_cloud < 0:
                                special_cloud_list.append('NIL')
                                got_special_cloud = idx
                else:
                    if got_temp < 0:
                        found_temp, got_temp, temperature_list, dewpoint_list = \
                            temp_tau_check(
                                metar[latest_idx:idx],
                                got_temp,
                                temperature_list,
                                dewpoint_list,
                                idx
                            )
                        if found_temp == True:
                            if got_cloud_1 < 0:
                                cloud_list_1.append('NIL')
                                got_cloud_1 = idx
                            if got_cloud_2 < 0:
                                cloud_list_2.append('NIL')
                                got_cloud_2 = idx
                            if got_cloud_3 < 0:
                                cloud_list_3.append('NIL')
                                got_cloud_3 = idx
                            if got_special_cloud < 0:
                                special_cloud_list.append('NIL')
                                got_special_cloud = idx

                if got_temp > 0 and idx != got_temp:
                    for pressure in pressure_unit:
                        if pressure in metar[latest_idx:idx] and metar[latest_idx:idx] not in wx_unit:
                            pressure_list.append(metar[latest_idx:idx])
                            got_pressure = idx

                if got_pressure > 0 and idx != got_pressure and got_trend < 0:
                    trend_list.append(metar[latest_idx:-2])
                    got_trend = idx

                #End of Sort
                latest_idx = idx

        if got_temp > 0 and got_pressure <0:
            print(metar[latest_idx:idx])

        #End of METAR
        if got_wind_var<0:
            var_wind_list.append('-99V-99')
        if got_cloud_1<0:
            cloud_list_1.append('NIL')
        if got_cloud_2<0:
            cloud_list_2.append('NIL')
        if got_cloud_3<0:
            cloud_list_3.append('NIL')
        if got_special_cloud<0:
            special_cloud_list.append('NIL')
        if got_sig_weather<0:
            sig_weather_list.append('NIL')
        if got_sig_weather_2<0:
            sig_weather_list_2.append('NIL')
        if got_sig_weather_3<0:
            sig_weather_list_3.append('NIL')
        if got_pressure<0:
            pressure_list.append('QNIL')
        if got_trend<0:
            trend_list.append('NIL')

        auto_mode = False
        cavok_mode = False
        wind_mode = ''
        latest_idx = 0
        got_wind = -99
        got_wind_var = -99
        got_cloud_1 = -99
        got_cloud_2 = -99
        got_cloud_3 = -99
        got_special_cloud = -99
        got_sig_weather = -99
        got_sig_weather_2 = -99
        got_sig_weather_3 = -99
        got_vis = -99
        got_vis_min = -99
        got_temp = -99
        got_pressure = -99
        got_trend = -99

    print(len(wind_list))
    print(len(date_list))
    print(len(var_wind_list))
    print(len(vis_list))
    print(len(vis_min_list))
    print(len(sig_weather_list))
    print(len(sig_weather_list_2))
    print(len(sig_weather_list_3))

    print(len(cloud_list_1))
    print(cloud_list_1)
    print(len(cloud_list_2))
    print(cloud_list_2)
    print(len(cloud_list_3))
    print(cloud_list_3)
    print(len(special_cloud_list))
    print(special_cloud_list)
    print(len(temperature_list))
    print(temperature_list)
    print(len(dewpoint_list))
    print(dewpoint_list)
    print(len(pressure_list))
    print(pressure_list)
    print(len(trend_list))
    print(trend_list)


    da_wind = xr.DataArray(wind_list, coords=dict(date=date_list),name='windspeed and direction')
    da_wind_var = xr.DataArray(var_wind_list, coords=dict(date=date_list),name='windvariation')
    da_vis = xr.DataArray(vis_list, coords=dict(date=date_list),name='visibility')
    da_vis_min = xr.DataArray(vis_min_list, coords=dict(date=date_list),name='visibility min')
    da_sig_weather_1 = xr.DataArray(sig_weather_list, coords=dict(date=date_list),name='significant weather')
    da_sig_weather_2 = xr.DataArray(sig_weather_list_2, coords=dict(date=date_list),name='significant weather 2')
    da_sig_weather_3 = xr.DataArray(sig_weather_list_3, coords=dict(date=date_list),name='significant weather 3')
    da_cloud_1 = xr.DataArray(cloud_list_1, coords=dict(date=date_list),name='cloud level 1')
    da_cloud_2 = xr.DataArray(cloud_list_2, coords=dict(date=date_list),name='cloud level 2')
    da_cloud_3 = xr.DataArray(cloud_list_3, coords=dict(date=date_list),name='cloud level 3')
    da_sig_cloud = xr.DataArray(special_cloud_list, coords=dict(date=date_list),name='significant cloud')
    da_temperature = xr.DataArray(temperature_list, coords=dict(date=date_list),name='temperature')
    da_dewpoint = xr.DataArray(dewpoint_list, coords=dict(date=date_list),name='dewpoint')
    da_pressure = xr.DataArray(pressure_list, coords=dict(date=date_list),name='pressure')
    da_trend = xr.DataArray(trend_list, coords=dict(date=date_list),name='trend')

    ds_wind = da_wind.to_dataset(name='windspeed_direction')
    ds_wind_var = da_wind_var.to_dataset(name='windvariation')
    ds_vis = da_vis.to_dataset(name='visibility')
    ds_vis_min = da_vis_min.to_dataset(name='visibility_min')
    ds_sig_weather_1 = da_sig_weather_1.to_dataset(name='significant_weather')
    ds_sig_weather_2 = da_sig_weather_2.to_dataset(name='significant_weather_2')
    ds_sig_weather_3 = da_sig_weather_3.to_dataset(name='significant_weather_3')
    ds_cloud_1 = da_cloud_1.to_dataset(name='cloud_level_1')
    ds_cloud_2 = da_cloud_2.to_dataset(name='cloud_level_2')
    ds_cloud_3 = da_cloud_3.to_dataset(name='cloud_level_3')
    ds_sig_cloud = da_sig_cloud.to_dataset(name='significant_cloud')
    ds_temperature = da_temperature.to_dataset(name='temperature')
    ds_dewpoint = da_dewpoint.to_dataset(name='dewpoint')
    ds_pressure = da_pressure.to_dataset(name='pressure')
    ds_trend = da_trend.to_dataset(name='trend')

    ds_all = ds_wind.merge(ds_wind_var)
    ds_all = ds_all.merge(ds_vis)
    ds_all = ds_all.merge(ds_vis_min)
    ds_all = ds_all.merge(ds_sig_weather_1)
    ds_all = ds_all.merge(ds_sig_weather_2)
    ds_all = ds_all.merge(ds_sig_weather_3)
    ds_all = ds_all.merge(ds_cloud_1)
    ds_all = ds_all.merge(ds_cloud_2)
    ds_all = ds_all.merge(ds_cloud_3)
    ds_all = ds_all.merge(ds_sig_cloud)
    ds_all = ds_all.merge(ds_temperature)
    ds_all = ds_all.merge(ds_dewpoint)
    ds_all = ds_all.merge(ds_pressure)
    ds_all = ds_all.merge(ds_trend)

    return ds_all

def Parse_Taf(flugplatz, taf_list):

    latest = 0

    taf_base = True

    taf_base_idx = -99
    taf_forecast_idx = -99
    taf_forecast_range_idx = -99
    taf_wind_base_idx = -99
    taf_cloud_base_idx = -99
    taf_vis_base_idx = -99
    taf_sig_weather_base_idx = -99


    changing_groups = ['TEMPO','BECMG','FM']

    wind_unit = ['KT', 'MPS', 'KMH']
    pressure_unit = ['Q']
    cloud_unit = ['BKN','OVC','SCT','FEW','NSC','SKC']
    wx_unit = ['MI', 'BC', 'PR', 'DR', 'BL', 'SH', 'TS', 'FZ', 'DZ', 'RA', 'SN', 'SG'
        , 'PL', 'GR', 'GS', 'UP', 'BR', 'FG', 'FU', 'VA', 'DU', 'SA', 'HZ', 'PO'
        , 'SQ', 'FC', 'SS', 'DS', 'WS', 'IC', 'PY', 'VC', 'RE']

    issued_time_list = []
    forecast_range_list = []

    base_wind_list = []
    base_visibility_list = []
    base_sig_weather_list = []
    base_cloud_list = []

    time_change = []
    change_wind_list = []
    change_vis_list = []
    change_sig_weather_list = []
    change_cloud_list = []

    for taf in taf_list:

        if '/n' in taf:
            taf = taf.replace('/n','')

        print(taf)
        print('Analyse')

        for idx in range(0,len(taf)):
            if ' ' in taf[idx]:                         #Divide it into Parts
                if len(taf[latest:idx])>1:              #Show only Parts with length >0 (filter artefacts)
                    if flugplatz in taf[latest:idx]:    #If the ICAO part of the TAF -> Base
                        taf_base = True
                        taf_base_idx = idx

                    if taf_base == True:
                        if (taf_forecast_idx < 0
                            and 'Z' in taf[latest:idx]
                            and idx != taf_base_idx):

                                issued_time_list.append(taf[latest:idx])
                                taf_forecast_idx = idx

                        if (taf_forecast_idx > 0
                            and idx != taf_forecast_idx
                            and taf_forecast_range_idx < 0):
                            #Structure : ddhh/ddhh (FROM/TILL)
                            if "/" in taf[latest:idx]:
                                forecast_range_list.append(taf[latest:idx])
                                taf_forecast_range_idx = idx

                        if (taf_forecast_range_idx > 0
                            and idx != taf_forecast_range_idx)\
                            and taf_wind_base_idx < 0:
                            #Structure dirffGfxKT (direction,strength,gusts,Unit)
                                base_wind_list.append(taf[latest:idx])




                    print(taf[latest:idx])
                    latest = idx
                else:
                    latest = idx

        print(taf[latest:idx])

        taf_base_idx = -99
        taf_forecast_idx = -99
        taf_forecast_range_idx = -99

        latest = 0
    print(issued_time_list)
    print(forecast_range_list)

        #Structure : TAF LOCATIONID IUSSED DATE/TIMERANGE (!IMPORTANT) WIND VIS WEATHER CLOUDS
        # (Groups with changing)
        #print(taf)



# ToDo write this in a main func and use the if __name__ == '__main__':
#  condition. Otherwise this code is executed if you want to import it elsewhere
#  for a single file it is totally fine, but if you want to scale it makes it easier to
#  start that way
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

#dataset = Parse_Metar(metar)

#pre,ext = os.path.splitext(path)
#dataset.to_netcdf(pre+'.nc')

Parse_Taf(flugplatz,taf)

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


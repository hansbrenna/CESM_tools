#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 13:49:00 2018

@author: hanbre
"""

from __future__ import print_function
import numpy as np
import xarray as xr
import pandas as pd
import netCDF4
import matplotlib.pyplot as plt
import os
import glob

def days_since(refdate='0001-01-01',startdate='0001-01-01',stopdate='0003-01-01',res='m',calendar='noleap'):
    if res == 'm':
        day = 15
    else:
        day = None
        
    months = {'01':(0,30),'02':(31,58),'03':(59,89),'04':(90,119),'05':(120,150),'06':(151,180),'07':(181,211),
              '08':(212,242),'09':(243,272),'10':(273,303),'11':(304,333),'12':(334,364)}
    refyear,refmonth,refday = refdate.split('-')
    startyear,startmonth,startday = startdate.split('-')
    stopyear,stopmonth,stopday = stopdate.split('-')
    days_since = []
    year = int(startyear)
    while year < int(stopyear):
        print(year)
        for month in months.keys():
            days_since.append((year-1)*365+months[month][0]+day)
        year += 1
    days_since = days_since.sort()
    return days_since

def parse_file_name(f):
    file_name = f.split('_')
    emis_source = ['aircraft','anthro','bb','other','contvolcano','ship','biogenic']
    emis_type = ['vertical','surface','ar5vertical']
    emis_comp = ['bc_a4','CO','DMS','NO2','NO','num_bc4_a4','num_pom_a4','num_so4_a1','num_so4_a2','pom_a4','SO2','so4_a1','so4_a2','SOAG']
    res = '0.9x1.25'
    period = '1850-pi'
    extension = '.nc'
    for source in emis_source:
        if source in f:
            use_source = source
    for typ in emis_type:
        if typ in f:
            use_type = typ
    for comp in emis_comp:
        if comp in f:
            use_comp = comp
    
    return '{0}_{1}_{2}_{3}_{4}_{5}{6}'.format(file_name[0],use_comp,use_source,use_type,period,res,extension)

if __name__ == '__main__':
    file_list = glob.glob('../*1850.nc')
    
    days_0001=days_since(startdate='0001-01-01',stopdate='0002-01-01')
    days_9998 = days_since(startdate='9998-01-01',stopdate='9999-01-01')
    days_0001.extend(days_9998)
    days = days_0001
    print(days)
    
    time = xr.DataArray(days,dims='time',coords={'time':days})
    time.attrs['units']='days since 0001-01-01 00:00:00'
    time.attrs['calendar']='noleap'
    time.attrs['long_name'] = 'time'
    
    temp=time.to_dataset(name = 'temp')
    temp=xr.decode_cf(temp)
    datelist = [str(t).strip('00:00:00').strip().replace('-','') for t in list(temp['temp'].values)]
    
    date = xr.DataArray(np.array(datelist,dtype=int),coords={'time':time})
    date.attrs['units'] = 'YYYMMDD'
    date.attrs['long_name'] = 'date'
    
    for f in file_list:
        print(f)
        data = xr.open_dataset(f,decode_times=False)
        data_twice = xr.concat([data,data],dim='time')
        data_twice['time'] = time
        data_twice['date'] = date
        savestring = parse_file_name(f)
        print(savestring)
        data_twice.to_netcdf(savestring,mode='w',format='NETCDF3_CLASSIC')
        data.close()